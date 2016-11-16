from __future__ import print_function, division
import distutils.version as dver
import sys
import journal_v2200
import journal_v2202
import message

sys.path.append('../thirdparty')
import iso8601
del sys.path[-1]


v2200 = "2.2.00"
v2202 = "2.2.02"


def get_valid_versions(version_str):
  verobj = dver.StrictVersion(version_str)
  if verobj >= dver.StrictVersion(v2202):
    return [v2202, v2200]
  else:
    return [v2200]


def create_message(versions, data):
  if 'event' not in data:
    raise ValueError("invalid journal message data provided, no event key")
  # Try to get a message, fall back to a generic JournalMessage object
  eventdata = journal_messages.get(data['event'], {v2200: JournalMessage})
  for v in versions:
    if v in eventdata:
      return eventdata[v](data, version=v)
  raise ValueError("no valid versions detected for specified message")


class JournalMessage(message.Message):
  def __init__(self, data, version = v2200):
    if 'timestamp' not in data or 'event' not in data:
      raise ValueError("data provided to journal message does not provide event and/or timestamp")
    time = iso8601.parse_date(data['timestamp'])
    source = "journal_{}".format(version)
    super(JournalMessage, self).__init__(data, source=source, time=time)
    self.version = version

  @property
  def event(self):
    return str(self.data['event'])


journal_messages = {
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
  "JetConeBoost": {v2200: journal_v2200.JetConeBoostMessage},
  "JetConeDamage": {v2200: journal_v2200.JetConeDamageMessage},
  "LaunchFighter": {v2200: journal_v2200.LaunchFighterMessage},
  "LaunchSRV": {v2200: journal_v2200.LaunchSRVMessage},
  "Liftoff": {v2200: journal_v2200.LiftoffMessage},
  "LoadGame": {v2200: journal_v2200.LoadGameMessage},
  "Location": {v2202: journal_v2202.LocationMessage, v2200: journal_v2200.LocationMessage},
  "MarketBuy": {v2200: journal_v2200.MarketBuyMessage},
  "MarketSell": {v2200: journal_v2200.MarketSellMessage},
  "MassModuleStore": {v2200: journal_v2200.MassModuleStoreMessage},
  "MaterialCollected": {v2200: journal_v2200.MaterialCollectedMessage},
  "MaterialDiscarded": {v2200: journal_v2200.MaterialDiscardedMessage},
  "MaterialDiscovered": {v2200: journal_v2200.MaterialDiscoveredMessage},
  "MiningRefined": {v2200: journal_v2200.MiningRefinedMessage},
  "MissionAbandoned": {v2200: journal_v2200.MissionAbandonedMessage},
  "MissionAccepted": {v2200: journal_v2200.MissionAcceptedMessage},
  "MissionCompleted": {v2200: journal_v2200.MissionCompletedMessage},
  "MissionFailed": {v2200: journal_v2200.MissionFailedMessage},
  "ModuleBuy": {v2200: journal_v2200.ModuleBuyMessage},
  "ModuleRetrieve": {v2200: journal_v2200.ModuleRetrieveMessage},
  "ModuleSell": {v2200: journal_v2200.ModuleSellMessage},
  "ModuleSellRemote": {v2200: journal_v2200.ModuleSellRemoteMessage},
  "ModuleStore": {v2200: journal_v2200.ModuleStoreMessage},
  "ModuleSwap": {v2200: journal_v2200.ModuleSwapMessage},
  "NewCommander": {v2200: journal_v2200.NewCommanderMessage},
  "PVPKill": {v2200: journal_v2200.PVPKillMessage},
  "PayFines": {v2200: journal_v2200.PayFinesMessage},
  "PayLegacyFines": {v2200: journal_v2200.PayLegacyFinesMessage},
  "PowerplayCollect": {v2200: journal_v2200.PowerplayCollectMessage},
  "PowerplayDefect": {v2200: journal_v2200.PowerplayDefectMessage},
  "PowerplayDeliver": {v2200: journal_v2200.PowerplayDeliverMessage},
  "PowerplayFastTrack": {v2200: journal_v2200.PowerplayFastTrackMessage},
  "PowerplayJoin": {v2200: journal_v2200.PowerplayJoinMessage},
  "PowerplayLeave": {v2200: journal_v2200.PowerplayLeaveMessage},
  "PowerplaySalary": {v2200: journal_v2200.PowerplaySalaryMessage},
  "PowerplayVote": {v2200: journal_v2200.PowerplayVoteMessage},
  "PowerplayVoucher": {v2200: journal_v2200.PowerplayVoucherMessage},
  "Progress": {v2200: journal_v2200.ProgressMessage},
  "Promotion": {v2200: journal_v2200.PromotionMessage},
  "Rank": {v2200: journal_v2200.RankMessage},
  "RebootRepair": {v2200: journal_v2200.RebootRepairMessage},
  "ReceiveText": {v2200: journal_v2200.ReceiveTextMessage},
  "RedeemVoucher": {v2200: journal_v2200.RedeemVoucherMessage},
  "RefuelAll": {v2200: journal_v2200.RefuelAllMessage},
  "RefuelPartial": {v2200: journal_v2200.RefuelPartialMessage},
  "RepairAll": {v2200: journal_v2200.RepairAllMessage},
  "Repair": {v2200: journal_v2200.RepairMessage},
  "RestockVehicle": {v2200: journal_v2200.RestockVehicleMessage},
  "Resurrect": {v2200: journal_v2200.ResurrectMessage},
  "Scan": {v2200: journal_v2200.ScanMessage},
  "ScientificResearch": {v2200: journal_v2200.ScientificResearchMessage},
  "Screenshot": {v2200: journal_v2200.ScreenshotMessage},
  "SelfDestruct": {v2200: journal_v2200.SelfDestructMessage},
  "SellDrones": {v2200: journal_v2200.SellDronesMessage},
  "SellExplorationData": {v2200: journal_v2200.SellExplorationDataMessage},
  "SendText": {v2200: journal_v2200.SendTextMessage},
  "ShieldState": {v2200: journal_v2200.ShieldStateMessage},
  "ShipyardBuy": {v2200: journal_v2200.ShipyardBuyMessage},
  "ShipyardNew": {v2200: journal_v2200.ShipyardNewMessage},
  "ShipyardSell": {v2200: journal_v2200.ShipyardSellMessage},
  "ShipyardSwap": {v2200: journal_v2200.ShipyardSwapMessage},
  "ShipyardTransfer": {v2200: journal_v2200.ShipyardTransferMessage},
  "SupercruiseEntry": {v2200: journal_v2200.SupercruiseEntryMessage},
  "SupercruiseExit": {v2200: journal_v2200.SupercruiseExitMessage},
  "Synthesis": {v2200: journal_v2200.SynthesisMessage},
  "Touchdown": {v2200: journal_v2200.TouchdownMessage},
  "USSDrop": {v2200: journal_v2200.USSDropMessage},
  "Undocked": {v2200: journal_v2200.UndockedMessage},
  "VehicleSwitch": {v2200: journal_v2200.VehicleSwitchMessage},
  "WingAdd": {v2200: journal_v2200.WingAddMessage},
  "WingJoin": {v2200: journal_v2200.WingJoinMessage},
  "WingLeave": {v2200: journal_v2200.WingLeaveMessage},
}

