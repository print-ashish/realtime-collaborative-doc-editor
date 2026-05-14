import pytest
from app.ot_engine import transform, transform_against_history

def test_insert_insert_conflict():
    """Test: Two users insert at the exact same position."""
    # User 1 (ID: 1) inserts 'A' at pos 0
    op1 = {"user_id": 1, "op_type": "insert", "position": 0, "content": "A"}
    # User 2 (ID: 2) inserts 'B' at pos 0
    op2 = {"user_id": 2, "op_type": "insert", "position": 0, "content": "B"}
    
    # If User 1's op is the 'base', User 2's op must be transformed
    new_op2 = transform(op2, op1)
    
    # Since User 2 has a higher ID, their 'B' should shift to position 1
    assert new_op2["position"] == 1
    assert new_op2["content"] == "B"

def test_insert_delete_conflict():
    """Test: User 1 inserts where User 2 just deleted."""
    # User 1 inserts 'X' at pos 5
    op1 = {"user_id": 1, "op_type": "insert", "position": 5, "content": "X"}
    # User 2 deletes char at pos 2 (which is before User 1's insert)
    op2 = {"user_id": 2, "op_type": "delete", "position": 2, "content": None}
    
    # User 1's insert should shift BACKWARDS because a character before it was removed
    new_op1 = transform(op1, op2)
    assert new_op1["position"] == 4

def test_delete_delete_same_position():
    """Test: Both users delete the exact same character."""
    op1 = {"user_id": 1, "op_type": "delete", "position": 10, "content": None}
    op2 = {"user_id": 2, "op_type": "delete", "position": 10, "content": None}
    
    # If the character is already deleted by op1, op2 should be nullified (noop)
    new_op2 = transform(op2, op1)
    assert new_op2["op_type"] == "noop"

def test_multi_step_transformation():
    """Test: A very stale operation catching up through history."""
    # History of what happened on the server
    history = [
        {"user_id": 1, "op_type": "insert", "position": 0, "content": "H"},
        {"user_id": 1, "op_type": "insert", "position": 1, "content": "e"},
        {"user_id": 1, "op_type": "insert", "position": 2, "content": "l"},
    ]
    
    # A user who is still at revision 0 tries to insert '!' at the very start
    stale_op = {"user_id": 2, "op_type": "insert", "position": 0, "content": "!"}
    
    # Catch up through all 3 history events
    final_op = transform_against_history(stale_op, history)
    
    # Since User 2 (ID: 2) has higher ID than User 1 (ID: 1), 
    # and they both hit pos 0, User 2's '!' should shift past the new characters.
    assert final_op["position"] == 3
