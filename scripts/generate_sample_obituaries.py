import os
import json
import random
import openai
from sqlalchemy.orm import sessionmaker
from app.core.database import engine, Obituary

# Initialize OpenAI client
client = openai.OpenAI()

# Sample data for generating varied obituaries
first_names = ["John", "Mary", "Robert", "Patricia", "James", "Jennifer", "Michael", "Linda", "William", "Elizabeth"]
last_names = ["Smith", "Johnson", "Brown", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin"]
careers = ["Doctor", "Engineer", "Teacher", "Artist", "Musician", "Scientist", "Pilot", "Chef", "Writer", "Philanthropist"]
achievements = [
    "won a national award for excellence in their field",
    "mentored hundreds of young professionals",
    "wrote several influential books",
    "led groundbreaking research in their discipline",
    "pioneered new techniques that changed their industry",
    "volunteered tirelessly to help their community",
    "was honored for their contributions to public service",
    "helped design iconic structures in the city",
    "composed music that touched the hearts of many",
    "inspired a new generation with their passion"
]
community_impacts = [
    "volunteered at local shelters",
    "mentored underprivileged youth",
    "donated time and resources to charities",
    "advocated for social justice",
    "taught free classes in their expertise",
    "organized fundraisers for good causes",
    "helped build homes for the needy",
    "founded a community outreach program",
    "supported local education initiatives",
    "was a beloved member of the neighborhood"
]

# Function to generate a sample obituary using OpenAI
def generate_obituary():
    name = f"{random.choice(first_names)} {random.choice(last_names)}"
    birth_year = random.randint(1930, 1985)
    death_year = birth_year + random.randint(50, 90)
    career = random.choice(careers)
    achievement = random.choice(achievements)
    community_impact = random.choice(community_impacts)

    obituary_prompt = (
        f"Write a professional obituary for {name}, born in {birth_year} and passed away in {death_year}. "
        f"They had a career as a {career} and {achievement}. "
        f"They also made a significant impact on the community by {community_impact}."
    )

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "system", "content": "You are an obituary writer."},
                  {"role": "user", "content": obituary_prompt}],
        temperature=0.7,
    )
    
    generated_text = response.choices[0].message.content.strip()
    openai_score = random.uniform(70, 100)  # Simulating AI score
    teacher_score = random.uniform(60, 100)  # Simulating teacher's score
    final_score = (openai_score + teacher_score) / 2

    input_data = json.dumps({
        "name": name,
        "birth_year": birth_year,
        "death_year": death_year,
        "career": career,
        "achievement": achievement,
        "community_impact": community_impact
    })

    return input_data, generated_text, openai_score, teacher_score, final_score

# Insert sample obituaries into database
def insert_sample_obituaries(n=100):
    Session = sessionmaker(bind=engine)
    session = Session()
    
    for _ in range(n):
        input_data, generated_text, openai_score, teacher_score, final_score = generate_obituary()
        obituary = Obituary(
            input_data=input_data,
            generated_text=generated_text,
            openai_score=openai_score,
            teacher_score=teacher_score,
            final_score=final_score
        )
        session.add(obituary)
    
    session.commit()
    session.close()

if __name__ == "__main__":
    insert_sample_obituaries(10)  # Generates and inserts 10 sample obituaries