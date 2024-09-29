from brainstorm_shuffle import create_app

application = create_app({'SQLALCHEMY_DATABASE_URI': 'sqlite:///brainstorm.db',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False})