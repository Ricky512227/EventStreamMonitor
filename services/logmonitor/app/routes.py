"""

API Routes for Log Monitoring Dashboard

"""

from flask import jsonify, request, send_from_directory

import os

from typing import Dict, Any

from app.kafka_consumer import error_store

def register_routes(app, logger):

    """

    Register API routes for log monitoring

    Args:

        app: Flask application instance

        logger: Logger instance

    """

    # Register Grafana routes

    from app.grafana_integration import register_grafana_routes

    register_grafana_routes(app, logger)

    @app.route('/health', methods=['GET'])

    def health():

        """Health check endpoint"""

        return jsonify({

            'status': 'healthy',

            'service': 'log-monitor'

        }), 200

    @app.route('/api/v1/logs/errors', methods=['GET'])

    def get_errors():

        """

        Get recent error logs

        Query params:

            limit: Number of errors to return (default: 100)

            service: Filter by service name (optional)

        """

        try:

            limit = int(request.args.get('limit', 100))

            service = request.args.get('service', None)

            errors = error_store.get_errors(limit=limit, service=service)

            return jsonify({

                'errors': errors,

                'count': len(errors)

            }), 200

        except Exception as e:

            logger.error(f"Error getting logs: {e}")

            return jsonify({'error': str(e)}), 500

    @app.route('/api/v1/logs/stats', methods=['GET'])

    def get_stats():

        """Get error statistics"""

        try:

            stats = error_store.get_stats()

            return jsonify(stats), 200

        except Exception as e:

            logger.error(f"Error getting stats: {e}")

            return jsonify({'error': str(e)}), 500

    @app.route('/api/v1/logs/services', methods=['GET'])

    def get_services():

        """Get list of services with errors"""

        try:

            services = list(error_store.service_stats.keys())

            return jsonify({

                'services': services,

                'count': len(services)

            }), 200

        except Exception as e:

            logger.error(f"Error getting services: {e}")

            return jsonify({'error': str(e)}), 500

    @app.route('/api/v1/logs/errors/<service>', methods=['GET'])

    def get_service_errors(service: str):

        """Get errors for a specific service"""

        try:

            limit = int(request.args.get('limit', 100))

            errors = error_store.get_errors(limit=limit, service=service)

            return jsonify({

                'service': service,

                'errors': errors,

                'count': len(errors)

            }), 200

        except Exception as e:

            logger.error(f"Error getting service logs: {e}")

            return jsonify({'error': str(e)}), 500

    @app.route('/', methods=['GET'])

    def dashboard():

        """Serve dashboard HTML"""

        try:

            dashboard_path = os.path.join(os.path.dirname(__file__), 'dashboard.html')

            return send_from_directory(os.path.dirname(dashboard_path), 'dashboard.html')

        except Exception as e:

            logger.error(f"Error serving dashboard: {e}")

            return jsonify({'error': str(e)}), 500

    logger.info("Log monitoring routes registered")
