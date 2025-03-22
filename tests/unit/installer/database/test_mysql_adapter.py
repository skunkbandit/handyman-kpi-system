"""\nTest suite for MySQL database adapter.\n\nThis module contains comprehensive tests for the MySQL database adapter\nwith mocking to avoid requiring an actual MySQL server for testing.\n"""\n\nimport os\nimport sys\nimport unittest\nfrom unittest.mock import patch, MagicMock\n\n# Add the main project directory to the path\nsys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))\n\n# Import the get_adapter function\nfrom installer.shared.database.adapters import get_adapter\n\n\nclass TestMySQLAdapter(unittest.TestCase):\n    """Test MySQL database adapter with mocking."""\n    \n    def setUp(self):\n        """Set up test environment."""\n        # MySQL configuration\n        self.config = {\n            'host': 'localhost',\n            'port': '3306',\n            'user': 'root',\n            'password': 'password',\n            'name': 'test_handyman_kpi'\n        }\n        \n        # Simple schema for testing\n        self.schema = """\n        CREATE TABLE users (\n            id INT AUTO_INCREMENT PRIMARY KEY,\n            username VARCHAR(255) UNIQUE NOT NULL,\n            password_hash VARCHAR(255) NOT NULL,\n            salt VARCHAR(255) NOT NULL,\n            email VARCHAR(255),\n            is_admin TINYINT DEFAULT 0\n        );\n        """\n        \n        # Patch mysql.connector to avoid requiring an actual MySQL server\n        self.mysql_patcher = patch('installer.shared.database.adapters.mysql.mysql')\n        self.mock_mysql = self.mysql_patcher.start()\n        \n        # Set up the mock connector\n        self.mock_connection = MagicMock()\n        self.mock_cursor = MagicMock()\n        self.mock_connection.cursor.return_value = self.mock_cursor\n        self.mock_mysql.connector.connect.return_value = self.mock_connection\n        \n        # Successful connection test result\n        self.mock_cursor.fetchone.return_value = (1,)\n        \n        # Create adapter\n        self.adapter = get_adapter('mysql', self.config)\n    \n    def tearDown(self):\n        """Clean up test environment."""\n        self.mysql_patcher.stop()\n    \n    def test_adapter_creation(self):\n        """Test adapter creation."""\n        # Test with valid configuration\n        adapter = get_adapter('mysql', self.config)\n        self.assertIsNotNone(adapter)\n        self.assertEqual(adapter.host, self.config['host'])\n        self.assertEqual(adapter.port, int(self.config['port']))\n        self.assertEqual(adapter.user, self.config['user'])\n        self.assertEqual(adapter.password, self.config['password'])\n        self.assertEqual(adapter.database, self.config['name'])\n        \n        # Test with default configuration\n        adapter = get_adapter('mysql', {})\n        self.assertIsNotNone(adapter)\n        self.assertEqual(adapter.host, 'localhost')\n        self.assertEqual(adapter.port, 3306)\n        self.assertEqual(adapter.user, 'root')\n        self.assertEqual(adapter.password, '')\n        self.assertEqual(adapter.database, 'handyman_kpi')\n    \n    def test_connection(self):\n        """Test database connection."""\n        # Test connection with valid configuration\n        self.assertTrue(self.adapter.test_connection())\n        \n        # Verify mock was called with correct parameters\n        self.mock_mysql.connector.connect.assert_called_with(\n            host='localhost',\n            port=3306,\n            user='root',\n            password='password'\n        )\n        \n        # Verify SELECT 1 was executed\n        self.mock_cursor.execute.assert_called_with("SELECT 1")\n    \n    def test_connection_failure(self):\n        """Test connection failure scenarios."""\n        # Make connection fail\n        self.mock_mysql.connector.connect.side_effect = self.mock_mysql.connector.Error("Test error")\n        \n        # Test connection (should fail)\n        self.assertFalse(self.adapter.test_connection())\n        \n        # Reset side effect\n        self.mock_mysql.connector.connect.side_effect = None\n        \n        # Make query fail\n        self.mock_cursor.execute.side_effect = self.mock_mysql.connector.Error("Test error")\n        \n        # Test connection (should fail)\n        self.assertFalse(self.adapter.test_connection())\n        \n        # Reset side effect\n        self.mock_cursor.execute.side_effect = None\n        \n        # Make fetchone return invalid result\n        self.mock_cursor.fetchone.return_value = (0,)\n        \n        # Test connection (should fail)\n        self.assertFalse(self.adapter.test_connection())