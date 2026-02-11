"""Summarization engine using Azure OpenAI."""
from typing import Literal, Optional
from openai import AzureOpenAI
from backend.app.config import config
from backend.app.errors import SummarizationError
from backend.app.logger import app_logger


class SummarizerEngine:
    """Summarization engine using Azure OpenAI."""
    
    def __init__(self):
        """Initialize Azure OpenAI client."""
        try:
            self.client = AzureOpenAI(
                api_key=config.AZURE_OPENAI_API_KEY,
                api_version=config.AZURE_OPENAI_API_VERSION,
                azure_endpoint=config.AZURE_OPENAI_ENDPOINT
            )
            app_logger.info("Azure OpenAI client initialized")
        except Exception as e:
            app_logger.error(f"Failed to initialize Azure OpenAI client: {str(e)}")
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
            
            # Call Azure OpenAI
            app_logger.info(f"Generating {length} summary (max_tokens={max_tokens})")
            
            response = self.client.chat.completions.create(
                model=config.AZURE_OPENAI_DEPLOYMENT,
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
