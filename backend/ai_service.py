from openai import OpenAI
from config import Config
from personnages import get_character_by_id

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

def generate_evaluation(reports_history, id=0):
    prompt = f"""
    Voici les résumés des derniers jours :
    {reports_history}
    
    Analysez l'évolution et fournissez une évaluation constructive.
    """

    perso = get_character_by_id(id)
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": perso['role']},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content