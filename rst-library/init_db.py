from app import app, db, Book, Event
import datetime

def seed_data():
    with app.app_context():
        db.create_all()
        
        # Check if books already exist
        if Book.query.first() is None:
            books = [
                Book(title='Data Structures and Algorithms', author='Robert Lafore', category='Computer Science'),
                Book(title='Introduction to Machine Learning', author='Ethem Alpaydin', category='AI & ML'),
                Book(title='Quantum Physics for Beginners', author='Michael Brooks', category='Physics'),
                Book(title='Modern Web Development', author='Kyle Simpson', category='Web Development'),
                Book(title='Clean Code', author='Robert C. Martin', category='Computer Science'),
                Book(title='Deep Learning Illustrated', author='Jon Krohn', category='AI & ML'),
                Book(title='Astrophysics for People in a Hurry', author='Neil deGrasse Tyson', category='Physics'),
                Book(title='Eloquent JavaScript', author='Marijn Haverbeke', category='Web Development'),
            ]
            db.session.bulk_save_objects(books)
            print("Seeded books.")

        # Check if events already exist
        if Event.query.first() is None:
            events = [
                Event(title='Research Paper Writing Workshop', date=datetime.date(2026, 4, 15), time='14:00 - 16:00', location='Main Library, Room B12', description='Learn effective strategies for writing academic research papers.'),
                Event(title='Digital Resources Orientation', date=datetime.date(2026, 4, 20), time='10:00 - 11:30', location='Library Computer Lab', description='Tour of our digital databases, e-books, and research tools.'),
            ]
            db.session.bulk_save_objects(events)
            print("Seeded events.")
            
        db.session.commit()

if __name__ == '__main__':
    seed_data()
