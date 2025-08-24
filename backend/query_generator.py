# query_generator.py (Free local model using Prem-1B-SQL)

from premsql.generators import Text2SQLGeneratorHF

# Initialize the model once
generator = Text2SQLGeneratorHF(model_or_name_or_path="premai-io/prem-1B-SQL", device="cpu")

def generate_sql(question):
    """
    Converts a natural language question to SQL using a local model.
    """
    sql_query = generator.generate(question)
    return sql_query
