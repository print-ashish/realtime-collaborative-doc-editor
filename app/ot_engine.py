def apply_operation(current_text:str , op_type: str , position:int , content: str = None)-> str:
    new_text = current_text 
    if op_type == "insert":
        new_text = current_text[:position] + content + current_text[position:]
        
    
    elif op_type == "delete":
        new_text = current_text[:position] + current_text[position + 1 : ]


    return new_text