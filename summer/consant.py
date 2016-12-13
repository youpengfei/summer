from enum import Enum, unique


@unique
class DeployEnv(Enum):
    DEV = 1
    PRERELEASE = 2
    PROD = 3
