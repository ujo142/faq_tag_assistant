from google import genai



def init_vertex_ai(project_id: str, location: str = "us-central1"):
    return genai.Client(vertexai=True, project=project_id, location=location)
