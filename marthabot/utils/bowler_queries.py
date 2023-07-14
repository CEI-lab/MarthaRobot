from bowler import Query
import bowler_queries

root = "~/HSI/marthabot/"
file = root + "robot/"

pattern = """
    power< "print"
        trailer< "(" print_args=any* ")" >
    >
"""

(
    Query()
    .select(pattern)
    .modify(...)
    .execute()
)