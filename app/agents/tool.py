from app.models.db import driver


# Tool Schema
neo4j_tool = {
    "name": "neo4j_query_executor",
    "description": "Executes a Cypher query against the Neo4j database and returns results.",
    "input_schema": {
        "type": "object",
        "properties": {
            "cypher_query": {
                "type": "string",
                "description": "A valid Cypher query string to be executed on the Neo4j database."
            }
        },
        "required": ["cypher_query"]
    }
}


# Tool Function
async def run_cypher(cypher_query: str):

    async with driver.session() as session:
        result = await session.run(cypher_query)
        return [record.data() async for record in result]
