from openai import OpenAI
from config import Config

client = OpenAI(api_key=Config.OPENAI_API_KEY)

def generate_summary(answers):
    prompt = f"""
    Voici les réponses à trois questions sur la journée d'aujourd'hui :
    {answers}
    
    Générez un résumé concis et empathique de cette journée.
    """
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Vous êtes un assistant empathique qui analyse des journaux quotidiens."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def generate_evaluation(reports_history):
    prompt = f"""
    Voici les résumés des derniers jours :
    {reports_history}
    
    Analysez l'évolution et fournissez une évaluation constructive sur les tendances observées.
    """
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Vous êtes un analyste bienveillant qui évalue les tendances émotionnelles."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content