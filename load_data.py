import csv
from app import create_app, db
from app.models import Obituary

app = create_app()
with app.app_context():
    with open('data.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            obituary = Obituary(
                full_name=row['Full Name'],
                university=row['University Affiliation'],
                birth_date=row['Date of Birth'],
                death_date=row['Date of Death'],
                obituary_url=row['Obituary URL']
            )
            db.session.add(obituary)
        db.session.commit()
