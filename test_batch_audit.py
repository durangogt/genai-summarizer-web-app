"""Test script to demonstrate batch processing with audit logging.

This script shows how the enhanced batch processing feature logs:
- Timestamp (automatically via Loguru)
- User ID (explicitly passed)
- Action (what operation is being performed)
- Error details (comprehensive error information)
"""
import sys
import io
from backend.app.logger import log_audit_event, app_logger
from backend.app.summarizer.service import summarizer_service

# Create test files
def create_test_files():
    """Create sample test files for batch processing."""
    files = [
        (b"This is a test document about AI.", "test1.txt"),
        (b"Another document discussing machine learning.", "test2.txt"),
        (b"invalid pdf content", "bad.pdf"),  # This will fail
    ]
    return files

def test_batch_with_audit_logging():
    """Demonstrate batch processing with comprehensive audit logging."""
    print("\n" + "="*70)
    print("TESTING BATCH PROCESSING WITH AUDIT LOGGING")
    print("="*70 + "\n")
    
    # Test data
    user_id = "test_user_123"
    files = create_test_files()
    
    print(f"Processing {len(files)} files for user: {user_id}\n")
    
    try:
        # Call batch processing (this will log extensively)
        results = summarizer_service.summarize_batch(
            files,
            length="short",
            user_id=user_id
        )
        
        # Display results
        print("\n" + "-"*70)
        print("BATCH PROCESSING RESULTS:")
        print("-"*70 + "\n")
        
        for result in results:
            status = "✓ SUCCESS" if result["success"] else "✗ FAILED"
            print(f"{status} - {result['filename']}")
            if result["error"]:
                print(f"  Error: {result['error']}")
            if result["summary"]:
                print(f"  Summary: {result['summary'][:80]}...")
            print()
        
        # Summary statistics
        successful = sum(1 for r in results if r["success"])
        failed = sum(1 for r in results if not r["success"])
        
        print("-"*70)
        print(f"SUMMARY: {successful}/{len(files)} successful, {failed}/{len(files)} failed")
        print("-"*70 + "\n")
        
    except Exception as e:
        print(f"\n✗ Batch processing failed: {str(e)}\n")
        log_audit_event(
            action="test_batch",
            user_id=user_id,
            status="failed",
            error=str(e)
        )

def test_audit_logging_directly():
    """Test the audit logging function directly."""
    print("\n" + "="*70)
    print("TESTING AUDIT LOGGING FUNCTION")
    print("="*70 + "\n")
    
    # Test successful action
    print("1. Logging successful action...")
    log_audit_event(
        action="test_action",
        user_id="john_doe",
        status="success",
        details={
            "file_count": 5,
            "processing_time": "2.3s"
        }
    )
    
    # Test failed action
    print("2. Logging failed action...")
    log_audit_event(
        action="test_action",
        user_id="jane_smith",
        status="failed",
        details={
            "file_name": "document.pdf"
        },
        error="File size exceeds maximum limit"
    )
    
    # Test started action
    print("3. Logging action start...")
    log_audit_event(
        action="batch_upload",
        user_id="admin",
        status="started",
        details={
            "batch_size": 10
        }
    )
    
    print("\n✓ Audit logging tests completed\n")

def show_audit_log_format():
    """Display information about the audit log format."""
    print("\n" + "="*70)
    print("AUDIT LOG FORMAT")
    print("="*70 + "\n")
    
    print("Each audit log entry includes:")
    print("  • timestamp    - ISO format timestamp (UTC)")
    print("  • user_id      - Username or identifier")
    print("  • action       - Operation being performed")
    print("  • status       - 'started', 'success', 'failed', 'partial_success'")
    print("  • details      - Additional context (dict)")
    print("  • error        - Error message (if status='failed')")
    print("\nExample log format:")
    print("  AUDIT | timestamp=2026-02-13T10:15:30.123456 | user_id=john_doe |")
    print("        action=batch_summarization | status=success |")
    print("        total_files=5 | successful=4 | failed=1")
    print()

if __name__ == "__main__":
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "BATCH PROCESSING AUDIT LOGGING TEST" + " "*18 + "║")
    print("╚" + "="*68 + "╝")
    
    show_audit_log_format()
    test_audit_logging_directly()
    
    print("\n" + "="*70)
    print("NOTE: The actual batch test is disabled as it requires AI credentials.")
    print("To test with real summarization, ensure GITHUB_TOKEN is set in .env")
    print("="*70 + "\n")
    
    # Uncomment to test with real AI (requires credentials):
    # test_batch_with_audit_logging()
    
    print("✓ All audit logging demonstrations completed successfully!\n")
