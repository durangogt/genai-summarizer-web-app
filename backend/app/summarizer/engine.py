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
        except Exception as e:
            app_logger.error(f"Failed to initialize GitHub Models client: {str(e)}")
            raise SummarizationError(f"Failed to initialize summarization engine: {str(e)}")
    
    def summarize(
        self, 
        text: str, 
        length: Literal["short", "medium", "long"] = "medium"
    ) -> str:
        """
        Generate summary of the provided text.
        
        Args:
            text: Text to summarize
            length: Summary length (short, medium, or long)
            
        Returns:
            Generated summary as string
            
        Raises:
            SummarizationError: If summarization fails
        """
        try:
            # Validate length parameter
            if length not in config.SUMMARY_LENGTHS:
                app_logger.warning(f"Invalid length '{length}', using default 'medium'")
                length = "medium"
            
            # Get configuration for requested length
            length_config = config.SUMMARY_LENGTHS[length]
            max_tokens = length_config["max_tokens"]
            
            # Prepare system message
            system_message = (
                "You are a helpful assistant that creates clear, concise summaries. "
                f"Provide a {length} summary that captures the key points and main ideas."
            )
            
            # Prepare user message
            user_message = f"Please summarize the following text:\n\n{text}"
            
            # Call GitHub Models with retry + exponential backoff
            app_logger.info(f"Generating {length} summary (max_tokens={max_tokens})")
            
            last_exception: Optional[Exception] = None
            for attempt in range(1, _MAX_RETRIES + 1):
                try:
                    response = self.client.chat.completions.create(
                        model=config.GITHUB_MODEL_NAME,
                        messages=[
                            {"role": "system", "content": system_message},
                            {"role": "user", "content": user_message}
                        ],
                        max_tokens=max_tokens,
                        temperature=0.7
                    )
                    
                    # Extract summary from response
                    summary = response.choices[0].message.content.strip()
                    
                    if not summary:
                        raise SummarizationError("Generated summary is empty")
                    
                    app_logger.info(f"Summary generated successfully ({len(summary)} characters)")
                    return summary
                    
                except SummarizationError:
                    # Do not retry on empty-summary logic errors
                    raise
                except BadRequestError as e:
                    # Check if it's a token limit error
                    error_message = str(e).lower()
                    if "token" in error_message or "length" in error_message or "too long" in error_message:
                        app_logger.error(f"Token limit exceeded: {str(e)}")
                        raise TokenLimitExceededError(
                            "The input text is too long for the AI model. "
                            "Please try with a shorter document or select a shorter summary length."
                        )
                    else:
                        app_logger.error(f"Bad request to AI API: {str(e)}")
                        raise SummarizationError(f"AI service rejected the request: {str(e)}")
                except Exception as e:
                    last_exception = e
                    if attempt < _MAX_RETRIES:
                        delay = _BASE_DELAY_SECONDS * (_BACKOFF_FACTOR ** (attempt - 1))
                        app_logger.warning(
                            f"AI API call failed (attempt {attempt}/{_MAX_RETRIES}): {str(e)}. "
                            f"Retrying in {delay:.1f}s..."
                        )
                        time.sleep(delay)
                    else:
                        app_logger.error(
                            f"AI API call failed after {_MAX_RETRIES} attempts: {str(e)}"
                        )
            
            # All retries exhausted
            raise APIConnectionError(
                f"The AI service is temporarily unavailable after {_MAX_RETRIES} attempts. "
                "Please try again later."
            )
            
        except (SummarizationError, APIConnectionError):
            raise
        except Exception as e:
            app_logger.error(f"Summarization failed: {str(e)}")
            raise SummarizationError(f"Failed to generate summary: {str(e)}")
    
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
        results = []
        
        for idx, text in enumerate(texts):
            try:
                summary = self.summarize(text, length)
                results.append({
                    "index": idx,
                    "success": True,
                    "summary": summary,
                    "error": None
                })
                app_logger.info(f"Batch item {idx + 1}/{len(texts)} summarized successfully")
            except Exception as e:
                app_logger.error(f"Batch item {idx + 1}/{len(texts)} failed: {str(e)}")
                results.append({
                    "index": idx,
                    "success": False,
                    "summary": None,
                    "error": str(e)
                })
        
        return results


# Global engine instance
summarizer_engine = SummarizerEngine()
