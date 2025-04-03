from langchain_core.tools import tool

@tool
def multiplication_tool(a: int, b: int = 1) -> int:
    """
    Takes two integer values and returns the multiplication of the two integers.

    Args:
        a (int) : first integer value
        b (int) : second integer value (if not provided then default value is 1)

    Returns:
        result (int) : returns a integer value that is the multiplication of the both the integers
    """
    result = a*b

    return f"Mulitplication result of {a}x{b} = {result}", [result]