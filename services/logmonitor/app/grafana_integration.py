"""
Grafana Integration for Log Monitoring
Provides data source API compatible with Grafana
"""
from flask import jsonify, request
from datetime import datetime, timedelta
from app.kafka_consumer import error_store


def register_grafana_routes(app, logger):
    """
    Register Grafana-compatible API routes
    
    Grafana expects specific response formats for data sources
    """
    
    @app.route('/api/v1/grafana/search', methods=['POST'])
    def grafana_search():
        """
        Grafana search endpoint - returns available metrics/fields
        """
        try:
            # Return available fields/metrics
            return jsonify([
                'error_count',
                'error_by_service',
                'error_by_level',
                'recent_errors'
            ]), 200
        except Exception as e:
            logger.error(f"Grafana search error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/v1/grafana/query', methods=['POST'])
    def grafana_query():
        """
        Grafana query endpoint - returns time series data
        """
        try:
            req_data = request.get_json()
            targets = req_data.get('targets', [])
            time_range = req_data.get('range', {})
            
            # Parse time range
            from_time = datetime.fromisoformat(
                time_range.get('from', {}).replace('Z', '+00:00')
            )
            to_time = datetime.fromisoformat(
                time_range.get('to', {}).replace('Z', '+00:00')
            )
            
            results = []
            
            for target in targets:
                target_type = target.get('target', 'error_count')
                
                if target_type == 'error_count':
                    # Return error count over time
                    stats = error_store.get_stats()
                    results.append({
                        'target': 'error_count',
                        'datapoints': [[stats['total_errors'], int(to_time.timestamp() * 1000)]]
                    })
                
                elif target_type == 'error_by_service':
                    # Return errors by service
                    service_stats = error_store.service_stats
                    for service, count in service_stats.items():
                        results.append({
                            'target': f'errors_{service}',
                            'datapoints': [[count, int(to_time.timestamp() * 1000)]]
                        })
                
                elif target_type == 'error_by_level':
                    # Return errors by level
                    level_stats = error_store.error_stats
                    for level, count in level_stats.items():
                        results.append({
                            'target': f'errors_{level}',
                            'datapoints': [[count, int(to_time.timestamp() * 1000)]]
                        })
            
            return jsonify(results), 200
        except Exception as e:
            logger.error(f"Grafana query error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/v1/grafana/annotations', methods=['POST'])
    def grafana_annotations():
        """
        Grafana annotations endpoint - for marking events on timeline
        """
        try:
            req_data = request.get_json()
            query = req_data.get('query', {})
            
            # Get recent errors as annotations
            errors = error_store.get_errors(limit=100)
            annotations = []
            
            for error in errors:
                timestamp = datetime.fromisoformat(
                    error.get('timestamp', datetime.utcnow().isoformat())
                    .replace('Z', '+00:00')
                )
                annotations.append({
                    'annotation': error.get('message', '')[:50],
                    'time': int(timestamp.timestamp() * 1000),
                    'title': f"{error.get('level', 'ERROR')} - {error.get('service', 'unknown')}",
                    'tags': [error.get('level', 'ERROR'), error.get('service', 'unknown')]
                })
            
            return jsonify(annotations), 200
        except Exception as e:
            logger.error(f"Grafana annotations error: {e}")
            return jsonify({'error': str(e)}), 500
    
    logger.info("Grafana integration routes registered")

