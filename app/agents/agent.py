from app.agents.tool import neo4j_tool, run_cypher
from app.config import settings
from anthropic import Anthropic


class Neo4jAgent:
    def __init__(self):
        self.client = Anthropic(api_key = settings.ANTHROPIC_API_KEY)
        self.tools = [neo4j_tool]

    async def agent_pipeline(self, user_query: str) -> str:
        response = self.client.messages.create(
            model="claude-3-haiku-20240307",
            tools=self.tools,
            system=("""
                You are an assistant that translates natural language into Neo4j Cypher queries
                and executes them via the neo4j_tool after generating the query.

                Schema:
                (:Make {name: string})
                (:Model {name: string})
                (:Year {value: integer})
                (:Category {name: string})

                Relationships:
                (:Make)-[:HAS_MODEL]->(:Model)
                (:Model)-[:AVAILABLE_IN]->(:Year)
                (:Model)-[:HAS_CATEGORY]->(:Category)

                Rules:
                - Always use the correct property names:
                  Make → name
                  Model → name
                  Year → value
                  Category → name
                - Always produce a valid Cypher query.
                - Do not explain the query. Call the tool with the Cypher query.
            """),
            messages=[{"role": "user", "content": user_query}],
            max_tokens=400,
        )

        # Check if the model requested a tool call
        tool_calls = [block for block in response.content if block.type == "tool_use"]

        if tool_calls:
            tool_call = tool_calls[0]
            cypher_query = tool_call.input["cypher_query"]

            # Execute the tool
            results = await run_cypher(cypher_query)

            # Format results into natural language
            answer = await self.results_to_nl(user_query, results)
            return answer

        else:
            return "No tool call detected."

    async def results_to_nl(self, user_query: str, results: list) -> str:
    
        response = self.client.messages.create(
            model="claude-3-haiku-20240307",
            system="You are an assistant that explains database results clearly in natural language.",
            messages=[
                {
                    "role": "user",
                    "content": f"Question: {user_query}\nResults: {results}\n\nFormat the answer nicely for a human."
                }
            ],
            max_tokens=400,
        )
        return response.content[0].text.strip()
    