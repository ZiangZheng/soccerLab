from isaaclab.assets import ArticulationCfg, AssetBaseCfg
from robotlib.soccerLab.mosc9 import MOSC9_CFG

from ..velocity_env_cfg import RobotEnvCfg
from ..velocity_env_cfg import RobotPlayEnvCfg

class MOSCFlatEnvCfg(RobotEnvCfg):
    def __post_init__(self):
        super().__post_init__()
        self.scene.robot = MOSC9_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")
        self.scene.height_scanner = None
        
        # self.rewards.joint_deviation_arms.params["asset_cfg"].joint_names = ["b_Ls", "b_Rs", "Ls_La", "Rs_Ra", "La_Lh", "Ra_Rh"]
        self.rewards.joint_deviation_arms = None
        # self.rewards.joint_deviation_waists.params["asset_cfg"].joint_names = ["b_n", "n_h"]
        self.rewards.joint_deviation_waists = None
        self.rewards.joint_deviation_legs.params["asset_cfg"].joint_names = ["Lh_Ll", "Rh_Rl", "Ll_Ll1", "Rl_Rl1"]

        self.rewards.feet_clearance.params["asset_cfg"].body_names = [".*foot"]
        self.rewards.feet_slide.params["asset_cfg"].body_names = [".*foot"]
        
        self.rewards.gait.params["sensor_cfg"].body_names = [".*foot"]
        self.rewards.feet_slide.params["sensor_cfg"].body_names = [".*foot"]
        self.rewards.undesired_contacts.params["sensor_cfg"].body_names = [".*ankle"]

        
        self.events.add_base_mass.params["asset_cfg"].body_names = "body"
        self.events.base_external_force_torque.params["asset_cfg"].body_names = "body"
        
        