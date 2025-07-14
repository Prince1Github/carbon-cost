from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Query

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///carbon.db'
db = SQLAlchemy(app)

class Emission(db.Model):
    """Database model for storing CO2 emission records"""
    id = db.Column(db.Integer, primary_key=True)
    repo = db.Column(db.String(100), nullable=False)
    owner = db.Column(db.String(100), nullable=False)
    run_id = db.Column(db.String(100), nullable=False)
    co2 = db.Column(db.Float, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    machine_type = db.Column(db.String(50), nullable=False)
    badge = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

@app.route('/record', methods=['POST'])
def record() -> tuple[Dict[str, str], int]:
    """
    Record a new CO2 emission from a CI/CD run
    
    Returns:
        JSON response with status and HTTP status code
    """
    try:
        data: Dict[str, Any] = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        emission = Emission(
            repo=data.get('repo', ''),
            owner=data.get('owner', ''),
            run_id=data.get('run_id', ''),
            co2=float(data.get('co2', 0)),
            duration=int(data.get('duration', 0)),
            machine_type=data.get('machine_type', ''),
            badge=data.get('badge', ''),
            timestamp=datetime.fromisoformat(data.get('timestamp', '').replace('Z', '+00:00'))
        )
        
        db.session.add(emission)
        db.session.commit()
        
        return jsonify({'status': 'success', 'id': emission.id}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/stats', methods=['GET'])
def stats() -> Dict[str, Any]:
    """
    Get comprehensive statistics about CO2 emissions
    
    Returns:
        JSON with total CO2, averages, badge counts, and emission list
    """
    try:
        emissions: List[Emission] = Emission.query.all()
        
        total_co2: float = sum(e.co2 for e in emissions)
        avg_co2: float = total_co2 / len(emissions) if emissions else 0
        
        badge_counts: Dict[str, int] = {
            badge: Emission.query.filter_by(badge=badge).count() 
            for badge in ['Green', 'Yellow', 'Red']
        }
        
        emissions_data: List[Dict[str, Any]] = [
            {
                'repo': e.repo,
                'owner': e.owner,
                'run_id': e.run_id,
                'co2': e.co2,
                'duration': e.duration,
                'machine_type': e.machine_type,
                'badge': e.badge,
                'timestamp': e.timestamp.isoformat()
            } for e in emissions
        ]
        
        return jsonify({
            'total_co2': total_co2,
            'average_co2': avg_co2,
            'badge_counts': badge_counts,
            'emissions': emissions_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/latest_co2_badge')
def latest_co2_badge() -> Dict[str, Any]:
    """
    Get the latest CO2 badge data for Shields.io integration
    
    Returns:
        JSON in Shields.io format with badge label, message, and color
    """
    try:
        latest: Optional[Emission] = Emission.query.order_by(
            Emission.timestamp.desc()
        ).first()
        
        if not latest:
            value = "No Data"
            color = "lightgrey"
        else:
            value = latest.badge
            color_map: Dict[str, str] = {
                "Green": "brightgreen", 
                "Yellow": "yellow", 
                "Red": "red"
            }
            color = color_map.get(latest.badge, "lightgrey")
        
        return jsonify({
            "schemaVersion": 1,
            "label": "CO2",
            "message": value,
            "color": color
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000) 