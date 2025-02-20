from openai import OpenAI
from config import Config
from personnages import get_character_by_id

client = OpenAI(api_key=Config.OPENAI_API_KEY)

def generate_summary(answers, objectifs):
    prompt = f"""
    Les objectifs du moment:
    {objectifs}
    L'humeur:
    {answers["mood"]}

    Voici les réponses à trois questions sur la journée d'aujourd'hui :
        _Qu'avez-vous accompli aujourd'hui ?
        réponse : {answers["q1"]}

        _Comment s'est passée votre journée ?
        réponse : {answers["q2"]}

        _Comment vous sentez-vous ce soir ?
        réponse : {answers["q3"]}
    
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
    Voici mes résumés des derniers jours :
    {reports_history}
    
    Analysez mon évolution et fournissez moi une évaluation constructive qui se termine par un son peu connu à découvrir.
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