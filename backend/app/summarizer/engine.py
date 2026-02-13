"""Summarization engine using GitHub Models."""
import time
from typing import Literal, Optional
from openai import OpenAI, BadRequestError
from backend.app.config import config
from backend.app.errors import SummarizationError, APIConnectionError, TokenLimitExceededError
from backend.app.logger import app_logger

# Retry configuration
_MAX_RETRIES = 3
_BASE_DELAY_SECONDS = 1.0
_BACKOFF_FACTOR = 2.0


class SummarizerEngine:
    """Summarization engine using GitHub Models."""
    
    def __init__(self):
        """Initialize GitHub Models client."""
        try:
            self.client = OpenAI(
                api_key=config.GITHUB_TOKEN,
                base_url=config.GITHUB_MODELS_ENDPOINT
            )
            app_logger.info("GitHub Models client initialized")
        except Exception as initialization_error:
            app_logger.error(f"Failed to initialize GitHub Models client: {str(initialization_error)}")
            raise SummarizationError(f"Failed to initialize summarization engine: {str(initialization_error)}")
    
    def _build_prompt_messages(self, input_text: str, length: str) -> list[dict]:
        """Build the system and user messages for the AI prompt.
        
        Args:
            input_text: Text to be summarized
            length: Summary length (short, medium, or long)
            
        Returns:
            List of message dictionaries for the AI API
        """
        system_message = (
            "You are a helpful assistant that creates clear, concise summaries. "
            f"Provide a {length} summary that captures the key points and main ideas."
        )
        user_message = f"Please summarize the following text:\n\n{input_text}"
        
        return [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    
    def summarize(
        self, 
        input_text: str, 
        length: Literal["short", "medium", "long"] = "medium"
    ) -> str:
        """
        Generate summary of the provided text.
        
        Args:
            input_text: Text to summarize
            length: Summary length (short, medium, or long)
            
        Returns:
            Generated summary as string
            
        Raises:
            SummarizationError: If summarization fails
        """
        app_logger.info(f"Starting summarization: input_length={len(input_text)} chars, requested_length={length}")
        
        try:
            # Validate length parameter
            if length not in config.SUMMARY_LENGTHS:
                app_logger.warning(f"Invalid length '{length}', using default 'medium'")
                length = "medium"
            
            # Get configuration for requested length
            length_config = config.SUMMARY_LENGTHS[length]
            max_tokens = length_config["max_tokens"]
            
            # Build AI prompt messages
            messages = self._build_prompt_messages(input_text, length)
            
            # Call GitHub Models with retry + exponential backoff
            app_logger.info(f"Calling AI API: length={length}, max_tokens={max_tokens}")
            
            last_exception: Optional[Exception] = None
            for attempt in range(1, _MAX_RETRIES + 1):
                try:
                    response = self.client.chat.completions.create(
                        model=config.GITHUB_MODEL_NAME,
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=0.7
                    )
                    
                    # Extract summary from response
                    generated_summary = response.choices[0].message.content.strip()
                    
                    if not generated_summary:
                        raise SummarizationError("Generated summary is empty")
                    
                    app_logger.info(
                        f"Summarization completed successfully: "
                        f"output_length={len(generated_summary)} chars, attempt={attempt}"
                    )
                    return generated_summary
                    
                except SummarizationError:
                    # Do not retry on empty-summary logic errors
                    raise
                except BadRequestError as token_error:
                    # Check if it's a token limit error
                    error_message = str(token_error).lower()
                    if "token" in error_message or "length" in error_message or "too long" in error_message:
                        app_logger.error(f"Token limit exceeded: {str(token_error)}")
                        raise TokenLimitExceededError(
                            "The input text is too long for the AI model. "
                            "Please try with a shorter document or select a shorter summary length."
                        )
                    else:
                        app_logger.error(f"Bad request to AI API: {str(token_error)}")
                        raise SummarizationError(f"AI service rejected the request: {str(token_error)}")
                except Exception as api_error:
                    last_exception = api_error
                    if attempt < _MAX_RETRIES:
                        delay = _BASE_DELAY_SECONDS * (_BACKOFF_FACTOR ** (attempt - 1))
                        app_logger.warning(
                            f"AI API call failed (attempt {attempt}/{_MAX_RETRIES}): {str(api_error)}. "
                            f"Retrying in {delay:.1f}s..."
                        )
                        time.sleep(delay)
                    else:
                        app_logger.error(
                            f"AI API call failed after {_MAX_RETRIES} attempts: {str(api_error)}"
                        )
            
            # All retries exhausted
            raise APIConnectionError(
                f"The AI service is temporarily unavailable after {_MAX_RETRIES} attempts. "
                "Please try again later."
            )
            
        except (SummarizationError, APIConnectionError, TokenLimitExceededError):
            raise
        except Exception as unexpected_error:
            app_logger.error(f"Unexpected summarization failure: {str(unexpected_error)}")
            raise SummarizationError(f"Failed to generate summary: {str(unexpected_error)}")
    
    def batch_summarize(
        self,
        texts: list[str],
        length: Literal["short", "medium", "long"] = "medium"
    ) -> list[dict]:
        """
        Generate summaries for multiple texts.
        
        Args:
            texts: List of texts to summarize
            length: Summary length for all texts
            
        Returns:
            List of dictionaries with 'text', 'summary', and 'success' keys
        """
        app_logger.info(f"Starting batch summarization: batch_size={len(texts)}, length={length}")
        results = []
        
        for idx, input_text in enumerate(texts):
            try:
                generated_summary = self.summarize(input_text, length)
                results.append({
                    "index": idx,
                    "success": True,
                    "summary": generated_summary,
                    "error": None
                })
                app_logger.info(f"Batch item {idx + 1}/{len(texts)} summarized successfully")
            except Exception as batch_error:
                app_logger.error(f"Batch item {idx + 1}/{len(texts)} failed: {str(batch_error)}")
                results.append({
                    "index": idx,
                    "success": False,
                    "summary": None,
                    "error": str(batch_error)
                })
        
        app_logger.info(f"Batch summarization completed: {sum(1 for r in results if r['success'])}/{len(texts)} successful")
        return results


# Global engine instance
summarizer_engine = SummarizerEngine()
