from typing import List, Union, Generator, Iterator
from pydantic import BaseModel
from schemas import OpenAIChatMessage
# This is a modified copy of URL: https://github.com/open-webui/pipelines/blob/main/examples/pipelines/integrations/wikipedia_pipeline.py

import requests
import os


class Pipeline:
    class Valves(BaseModel):
        pass

    def __init__(self):
        # Optionally, you can set the id and name of the pipeline.
        # Best practice is to not specify the id so that it can be automatically inferred from the filename, so that users can install multiple versions of the same pipeline.
        # The identifier must be unique across all pipelines.
        # The identifier must be an alphanumeric string that can include underscores or hyphens. It cannot contain spaces, special characters, slashes, or backslashes.
        # self.id = "wiki_pipeline"
        self.name = "Wikipedia Pipeline"

        # Initialize rate limits
        self.valves = self.Valves(**{"OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", "")})

    async def on_startup(self):
        # This function is called when the server is started.
        print(f"on_startup:{__name__}")
        pass

    async def on_shutdown(self):
        # This function is called when the server is stopped.
        print(f"on_shutdown:{__name__}")
        pass

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        # This is where you can add your custom pipelines like RAG.
        print(f"pipe:{__name__}")

        # Could add commands to configure the pipeline here
        if body.get("title", False):
            print("Title Generation")
            return "Wikipedia Pipeline"
        elif body.get("help", False):
            return "This is the help menu test"
        else:
            titles = []
            for query in [user_message]:
                # We should escape encode this not replace with _
                query = query.encode('unicode-escape')
            
                # Pull all titles for the topic limited to 1 result
                r = requests.get(
                    f"https://en.wikipedia.org/w/api.php?action=opensearch&search={query}&limit=1&namespace=0&format=json"
                )

                # Get response
                response = r.json()
                titles = titles + response[1]
                
                # Print out all the titles
                print(titles)

            # Setup the context that goes to the LLM
            context = user_message
            
            # If we have titles from above, get context data from wiki in json
            if len(titles) > 0:
                r = requests.get(
                    f"https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro&explaintext&redirects=1&titles={'|'.join(titles)}"
                )
                response = r.json()
                
                # get extracts and add them to the LLM context
                pages = response["query"]["pages"]
                for page in pages:
                    if context == None:
                        context = pages[page]["extract"] + "\n"
                    else:
                        context = context + pages[page]["extract"] + "\n"

            # Return new context from wiki
            return context if context else "No information found from wiki"
