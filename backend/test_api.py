#!/usr/bin/env python3
"""
Test script for BotParlay API
"""
import requests
from datetime import datetime, timedelta
import json

BASE_URL = "http://localhost:8000/api"

def test_create_bot():
    """Test bot creation"""
    print("Testing bot creation...")
    
    bot_data = {
        "name": "Claude-Test",
        "model_type": "Claude Sonnet 4.5",
        "specialization": "Philosophy and ethics",
        "api_endpoint": "https://api.anthropic.com/v1/messages"
    }
    
    response = requests.post(f"{BASE_URL}/bots", json=bot_data)
    print(f"Status: {response.status_code}")
    if response.ok:
        bot = response.json()
        print(f"Created bot: {bot['name']} (ID: {bot['id']})")
        return bot['id']
    else:
        print(f"Error: {response.text}")
        return None

def test_create_session(title, category, prompt):
    """Test session creation"""
    print(f"\nTesting session creation: {title}")
    
    session_data = {
        "title": title,
        "topic_category": category,
        "framing_prompt": prompt,
        "scheduled_time": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
        "duration_minutes": 60,
        "max_participants": 6,
        "created_by": "test-script"
    }
    
    response = requests.post(f"{BASE_URL}/sessions", json=session_data)
    print(f"Status: {response.status_code}")
    if response.ok:
        session = response.json()
        print(f"Created session: {session['title']} (ID: {session['id']})")
        return session['id']
    else:
        print(f"Error: {response.text}")
        return None

def test_register_bot(session_id, bot_id):
    """Test bot registration"""
    print(f"\nTesting bot registration for session {session_id}...")
    
    reg_data = {
        "bot_id": bot_id,
        "interest_statement": "I'm interested in exploring the philosophical implications of this topic."
    }
    
    response = requests.post(f"{BASE_URL}/sessions/{session_id}/register", json=reg_data)
    print(f"Status: {response.status_code}")
    if response.ok:
        registration = response.json()
        print(f"Registered bot {registration['bot_name']} for session")
        return True
    else:
        print(f"Error: {response.text}")
        return False

def test_list_sessions():
    """Test listing sessions"""
    print("\nTesting session listing...")
    
    response = requests.get(f"{BASE_URL}/sessions")
    print(f"Status: {response.status_code}")
    if response.ok:
        sessions = response.json()
        print(f"Found {len(sessions)} sessions")
        for s in sessions:
            print(f"  - {s['title']} ({s['status']}) - {s['participant_count']} participants")
        return sessions
    else:
        print(f"Error: {response.text}")
        return []

def run_tests():
    """Run all tests"""
    print("=" * 60)
    print("BotParlay API Test Suite")
    print("=" * 60)
    
    try:
        # Test bot creation
        bot_id = test_create_bot()
        if not bot_id:
            print("\nFailed to create bot. Stopping tests.")
            return
        
        # Test session creation (first two topics from our discussion)
        session1_id = test_create_session(
            "The Role of Uncertainty in AI Decision-Making",
            "AI Ethics",
            "When an AI system encounters uncertainty - incomplete information, ambiguous instructions, or conflicting data - how should it respond? Should it acknowledge uncertainty explicitly, make probabilistic judgments, defer to humans, or proceed with best-guess reasoning? What are the trade-offs?"
        )
        
        session2_id = test_create_session(
            "Should AI Systems Explain Their Reasoning?",
            "AI Ethics",
            "Transparency vs. performance: Should AI systems always explain how they reached conclusions? When are post-hoc explanations valuable vs. misleading? Does the obligation to explain depend on domain, stakes, or user sophistication? What are we really asking for when we demand 'explainability'?"
        )
        
        # Test registration
        if session1_id:
            test_register_bot(session1_id, bot_id)
        
        # List all sessions
        test_list_sessions()
        
        print("\n" + "=" * 60)
        print("All tests completed successfully!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to API server.")
        print("Make sure the server is running: uvicorn main:app --host 0.0.0.0 --port 8000")

if __name__ == "__main__":
    run_tests()
