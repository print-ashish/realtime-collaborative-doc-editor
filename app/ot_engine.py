def apply_operation(current_text:str , op_type: str , position:int , content: str = None)-> str:
    new_text = current_text 
    if op_type == "insert":
        new_text = current_text[:position] + content + current_text[position:]
        
    
    elif op_type == "delete":
        new_text = current_text[:position] + current_text[position + 1 : ]


    return new_text

def transform(incoming: dict, base: dict) -> dict:
    """
    Adjusts the 'incoming' operation based on what 'base' operation already did.
    """
    new_op = incoming.copy()
    
    # --- LEVEL 1: Check what the INCOMING operation is ---
    if incoming["op_type"] == "insert":
        
        # --- LEVEL 2: Compare against the BASE operation ---
        if base["op_type"] == "insert":
            if base["position"] < incoming["position"]:
                new_op["position"] += len(base["content"])
            elif base["position"] == incoming["position"]:
                # Tie-breaker
                if incoming["user_id"] > base["user_id"]:
                    new_op["position"] += len(base["content"])
        
        elif base["op_type"] == "delete":
            if base["position"] < incoming["position"]:
                new_op["position"] -= 1

    # --- LEVEL 1: Check what the INCOMING operation is ---
    elif incoming["op_type"] == "delete":
        
        # --- LEVEL 2: Compare against the BASE operation ---
        if base["op_type"] == "insert":
            if base["position"] <= incoming["position"]:
                new_op["position"] += len(base["content"])
        
        elif base["op_type"] == "delete":
            if base["position"] < incoming["position"]:
                new_op["position"] -= 1
            elif base["position"] == incoming["position"]:
                new_op["op_type"] = "noop" 

    return new_op

def transform_against_history(incoming_op: dict, history: list) -> dict:
    """
    Takes an incoming operation and transforms it against a list of 
    operations that happened since the client last synced.
    """
    transformed_op = incoming_op.copy()
    
    for base_op in history:
        # Handle both SQLAlchemy objects AND dictionaries (for testing)
        if isinstance(base_op, dict):
            base_op_dict = base_op
        else:
            base_op_dict = {
                "op_type": base_op.op_type,
                "position": base_op.position,
                "content": base_op.content,
                "user_id": base_op.user_id
            }
        
        transformed_op = transform(transformed_op, base_op_dict)
        
        # If the op becomes a no-op, we can stop
        if transformed_op["op_type"] == "noop":
            break
            
    return transformed_op
