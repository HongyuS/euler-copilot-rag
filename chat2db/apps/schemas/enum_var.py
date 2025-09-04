from enum import Enum


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DatabaseType(str, Enum):
    MYSQL = "mysql"
    POSTGRES = "postgres"
    OPENGAUSS = "opengauss"
    MONGODB = "mongodb"

if __name__ == "__main__":
    print(DatabaseType.MYSQL)
    print(DatabaseType.MYSQL.value)