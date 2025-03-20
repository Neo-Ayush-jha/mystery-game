import google.generativeai as genai
import random
from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Case, Suspect, Evidence

# Configure Gemini API
# genai.configure(api_key="YOUR_GEMINI_API_KEY")
genai.configure(api_key="AIzaSyBzMqKGU0PcloCb6mhP8sf8f8GHqqCrmEw")
model = genai.GenerativeModel("gemini-1.5-pro")

@api_view(["POST"])
def generate_case(request):
    """
    Generates a crime case in the user's chosen language using Google Gemini and saves it in the database.
    """
    # Get language from request, default to English
    language = request.data.get("language", "English")

    prompt = f"""
    Generate a unique crime case in {language}. Follow this exact format:
    
    Title: [Crime Title]
    Description: [Short crime description]

    Suspect 1: Name - [Suspect Name], Alibi - [Suspect Alibi]
    Suspect 2: Name - [Suspect Name], Alibi - [Suspect Alibi]
    Suspect 3: Name - [Suspect Name], Alibi - [Suspect Alibi]

    Evidence 1: [Evidence Description], Key Evidence - [Yes/No]
    Evidence 2: [Evidence Description], Key Evidence - [Yes/No]

    Crime Execution: [Describe exactly how the crime was committed]
    Culprit's Actions: [Explain how the guilty suspect planned and executed the crime]

    Ensure that title, description, suspects, evidence, and crime execution details are always present. The response should be entirely in {language}.
    """

    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()

        # Split response into lines
        case_data = response_text.split("\n")

        # Extract title and description
        title, description, crime_execution, culprit_actions = "", "", "", ""
        for line in case_data:
            if line.startswith("Title: "):
                title = line.replace("Title: ", "").strip()
            elif line.startswith("Description: "):
                description = line.replace("Description: ", "").strip()
            elif line.startswith("Crime Execution: "):
                crime_execution = line.replace("Crime Execution: ", "").strip()
            elif line.startswith("Culprit's Actions: "):
                culprit_actions = line.replace("Culprit's Actions: ", "").strip()

        # Validate extracted values
        if not title or not description or not crime_execution or not culprit_actions:
            return Response({"error": f"Missing required fields in AI response (Language: {language})"}, status=500)

        # Create case
        case = Case.objects.create(
            title=title, description=description, crime_execution=crime_execution, culprit_actions=culprit_actions
        )

        # Extract suspects
        guilty_suspect = None
        for line in case_data:
            if line.startswith("Suspect"):
                parts = line.split(", Alibi - ")
                if len(parts) < 2:
                    continue

                name = parts[0].split(" - ")[1].strip()
                alibi = parts[1].strip()
                is_guilty = random.choice([True, False])

                suspect = Suspect.objects.create(
                    case=case, name=name, alibi=alibi, is_guilty=is_guilty, age=random.randint(25, 60)
                )
                if is_guilty:
                    guilty_suspect = suspect

        # Extract evidence
        for line in case_data:
            if line.startswith("Evidence"):
                parts = line.split(", Key Evidence - ")
                if len(parts) < 2:
                    continue

                description = parts[0].replace("Evidence ", "").strip()
                is_key_evidence = parts[1].strip().lower() == "yes"

                Evidence.objects.create(case=case, description=description, is_key_evidence=is_key_evidence)

        return Response({
            "message": "Case generated!",
            "case_id": case.case_id,
            "title": case.title,
            "description": case.description,
            "crime_execution": case.crime_execution,
            "culprit_actions": case.culprit_actions,
            "language": language
        })

    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(["POST"])
def interrogate_suspect(request, suspect_id):
    """
    Interrogates a suspect using Google Gemini and returns an AI-generated response in the chosen language.
    """

    try:
        suspect = Suspect.objects.get(id=suspect_id)
    except Suspect.DoesNotExist:
        return Response({"error": "Suspect not found"}, status=404)

    question = request.data.get("question", "")
    language = request.data.get("language", "English")

    prompt = f"""
    You are a suspect in a detective game. Your name is {suspect.name}.
    You are being interrogated about a crime.

    Crime details: {suspect.case.description}
    Your alibi: {suspect.alibi}

    Player's question: "{question}"

    Respond as the suspect, staying in character. Respond in {language} only.
    """

    try:
        response = model.generate_content(prompt)
        ai_response = response.text.strip()

        return Response({"suspect": suspect.name, "response": ai_response, "language": language})

    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
def case_details(request, case_id):
    """
    Fetch complete details of a case, including suspects, evidence, and crime execution details.
    """
    try:
        # Fetch case
        case = Case.objects.get(case_id=case_id)

        # Fetch suspects related to this case
        suspects = case.suspects.all().values("id", "name", "age", "alibi", "is_guilty")

        # Fetch evidence related to this case
        evidence = case.evidence.all().values("id", "description", "is_key_evidence")

        # Construct response data
        data = {
            "case_id": case.case_id,
            "title": case.title,
            "description": case.description,
            "crime_execution": case.crime_execution,
            "culprit_actions": case.culprit_actions,
            "is_solved": case.is_solved,
            "created_at": case.created_at,
            "suspects": list(suspects),
            "evidence": list(evidence),
        }

        return Response(data, status=200)

    except Case.DoesNotExist:
        return Response({"error": "Case not found"}, status=404)