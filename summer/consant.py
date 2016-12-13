from enum import Enum, unique


@unique
class DeployEnv(Enum):
    DEV = 1
    PRE_RELEASE = 2
    PROD = 3
