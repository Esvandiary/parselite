from __future__ import print_function, division
import distutils.version as dver
import journal_v2200
import journal_v2202

v2200 = "2.2.00"
v2202 = "2.2.02"

def get_valid_versions(version_str):
  verobj = dver.StrictVersion(version_str)
  if verobj >= dver.StrictVersion(v2202):
    return [v2202, v2200]
  else:
    return [v2200]

messages = {
  "ApproachSettlement": {v2200: journal_v2200.ApproachSettlementMessage},
  "Bounty": {v2200: journal_v2200.BountyMessage},
  "BuyAmmo": {v2200: journal_v2200.BuyAmmoMessage},
  "BuyDrones": {v2200: journal_v2200.BuyDronesMessage},
  "BuyExplorationData": {v2200: journal_v2200.BuyExplorationDataMessage},
  "BuyTradeData": {v2200: journal_v2200.BuyTradeDataMessage},
  "CapShipBond": {v2200: journal_v2200.CapShipBondMessage},
  "ClearSavedGame": {v2200: journal_v2200.ClearSavedGameMessage},
  "CockpitBreached": {v2200: journal_v2200.CockpitBreachedMessage},
  "CollectCargo": {v2200: journal_v2200.CollectCargoMessage},
  "CommitCrime": {v2200: journal_v2200.CommitCrimeMessage},
  "CommunityGoalJoin": {v2200: journal_v2200.CommunityGoalJoinMessage},
  "CommunityGoalReward": {v2200: journal_v2200.CommunityGoalRewardMessage},
  "Continued": {v2200: journal_v2200.ContinuedMessage},
  "CrewAssign": {v2200: journal_v2200.CrewAssignMessage},
  "CrewFire": {v2200: journal_v2200.CrewFireMessage},
  "CrewHire": {v2200: journal_v2200.CrewHireMessage},
  "DataScanned": {v2200: journal_v2200.DataScannedMessage},
  "DatalinkScan": {v2200: journal_v2200.DatalinkScanMessage},
  "DatalinkVoucher": {v2200: journal_v2200.DatalinkVoucherMessage},
  "Died": {v2200: journal_v2200.DiedMessage},
  "DockFighter": {v2200: journal_v2200.DockFighterMessage},
  "DockSRV": {v2200: journal_v2200.DockSRVMessage},
  "Docked": {v2202: journal_v2202.DockedMessage, v2200: journal_v2200.DockedMessage},
  "DockingCancelled": {v2200: journal_v2200.DockingCancelledMessage},
  "DockingDenied": {v2200: journal_v2200.DockingDeniedMessage},
  "DockingGranted": {v2200: journal_v2200.DockingGrantedMessage},
  "DockingRequested": {v2200: journal_v2200.DockingRequestedMessage},
  "DockingTimeout": {v2200: journal_v2200.DockingTimeoutMessage},
  "EjectCargo": {v2200: journal_v2200.EjectCargoMessage},
  "EngineerApply": {v2200: journal_v2200.EngineerApplyMessage},
  "EngineerCraft": {v2200: journal_v2200.EngineerCraftMessage},
  "EngineerProgress": {v2200: journal_v2200.EngineerProgressMessage},
  "EscapeInterdiction": {v2200: journal_v2200.EscapeInterdictionMessage},
  "FSDJump": {v2202: journal_v2202.FSDJumpMessage, v2200: journal_v2200.FSDJumpMessage},
  "FactionKillBond": {v2200: journal_v2200.FactionKillBondMessage},
  "FetchRemoteModule": {v2200: journal_v2200.FetchRemoteModuleMessage},
  "Fileheader": {v2200: journal_v2200.FileheaderMessage},
  "FuelScoop": {v2200: journal_v2200.FuelScoopMessage},
  "HeatDamage": {v2200: journal_v2200.HeatDamageMessage},
  "HeatWarning": {v2200: journal_v2200.HeatWarningMessage},
  "HullDamage": {v2200: journal_v2200.HullDamageMessage},
  "Interdicted": {v2200: journal_v2200.InterdictedMessage},
  "Interdiction": {v2200: journal_v2200.InterdictionMessage},
  # TODO: ...
}