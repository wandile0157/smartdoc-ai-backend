"""
Simple API test script
Tests the local development server
"""

import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000/api/v1"


def print_result(title: str, response: requests.Response):
    """Print formatted response"""
    print("\n" + "=" * 60)
    print(f"📋 {title}")
    print("=" * 60)
    print(f"Status Code: {response.status_code}")
    
    try:
        response_json = response.json()
        print(f"\nResponse:")
        
        if response.status_code == 200:
            # Success - show main fields
            if "document_info" in response_json:
                print(f"Document Type: {response_json['document_info']['document_type']}")
            if "parties" in response_json:
                print(f"Parties Found: {len(response_json['parties'])}")
                for party in response_json['parties'][:3]:
                    print(f"  - {party['name']} ({party['role']})")
            if "monetary_amounts" in response_json:
                print(f"Amounts Found: {len(response_json['monetary_amounts'])}")
                for amount in response_json['monetary_amounts'][:3]:
                    print(f"  - {amount['amount']} ({amount['currency']})")
            if "risk_assessment" in response_json:
                risk = response_json['risk_assessment']
                print(f"Risk Score: {risk['risk_score']} - {risk['risk_level']}")
            if "sentiment" in response_json:
                sent = response_json['sentiment']
                print(f"Sentiment: {sent['sentiment']} (polarity: {sent['polarity']})")
            if "basic_stats" in response_json:
                stats = response_json['basic_stats']
                print(f"Word Count: {stats['word_count']}")
                print(f"Sentence Count: {stats['sentence_count']}")
        else:
            print(json.dumps(response_json, indent=2))
    except Exception as e:
        print(f"Error: {e}")


def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print_result("Health Check", response)


def test_text_analysis():
    """Test text analysis"""
    data = {
        "text": "SmartDoc AI is an innovative platform for South African businesses. It helps companies analyze legal documents quickly and accurately. Businesses in Johannesburg, Pretoria, and Cape Town are using this technology successfully.",
        "analysis_type": "text"
    }
    response = requests.post(f"{BASE_URL}/analyze/text", json=data)
    print_result("Text Analysis", response)


def test_feedback_analysis():
    """Test feedback analysis"""
    data = {
        "text": "The legal document analysis was incredibly helpful and accurate. It identified all the key terms, parties, and risks in seconds. However, the interface could be more intuitive. Overall, I'm very impressed with the technology and would recommend it to other law firms.",
        "source": "customer_review"
    }
    response = requests.post(f"{BASE_URL}/analyze/feedback", json=data)
    print_result("Feedback Analysis", response)


def test_legal_analysis():
    """Test legal analysis with employment contract"""
    sample_file = Path("sample_data/employment_contract.txt")
    
    if not sample_file.exists():
        print(f"\n❌ Sample file not found: {sample_file}")
        return
    
    try:
        with open(sample_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        data = {
            "text": text,
            "document_type": "employment_contract"
        }
        
        response = requests.post(f"{BASE_URL}/analyze/legal", json=data)
        print_result("Legal Document Analysis - Employment Contract", response)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


def test_legal_lease():
    """Test legal analysis with lease agreement"""
    sample_file = Path("sample_data/lease_agreement.txt")
    
    if not sample_file.exists():
        print(f"\n⚠️ Lease agreement file not found, skipping...")
        return
    
    try:
        with open(sample_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        data = {
            "text": text,
            "document_type": "lease_agreement"
        }
        
        response = requests.post(f"{BASE_URL}/analyze/legal", json=data)
        print_result("Legal Document Analysis - Lease Agreement", response)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


def test_legal_nda():
    """Test legal analysis with NDA"""
    sample_file = Path("sample_data/nda_agreement.txt")
    
    if not sample_file.exists():
        print(f"\n⚠️ NDA file not found, skipping...")
        return
    
    try:
        with open(sample_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        data = {
            "text": text,
            "document_type": "nda"
        }
        
        response = requests.post(f"{BASE_URL}/analyze/legal", json=data)
        print_result("Legal Document Analysis - NDA", response)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    print("\n🧪 SmartDoc AI - Comprehensive API Tests")
    print("=" * 60)
    print("Testing all endpoints...")
    print("=" * 60)
    
    try:
        test_health()
        test_text_analysis()
        test_feedback_analysis()
        
        print("\n" + "=" * 60)
        print("📄 Testing Legal Documents")
        print("=" * 60)
        
        test_legal_analysis()
        test_legal_lease()
        test_legal_nda()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
    
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to server")
        print("Make sure the server is running: python run.py")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")