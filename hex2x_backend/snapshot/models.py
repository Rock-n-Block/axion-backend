from django.db import models

from hex2x_backend.tokenholders.models import TokenStakeStart
# Create your models here.


class HexUser(models.Model):
    user_address = models.CharField(max_length=100)
    hex_amount = models.DecimalField(max_digits=len(str(2**256)), decimal_places=0, default=0)
    user_hash = models.CharField(max_length=256, null=True, default=None)
    hash_signature = models.CharField(max_length=256, null=True, default=None)
    snapshot_tx = models.CharField(max_length=256, null=True, default=None)
    tx_checked = models.BooleanField(default=False)


class SnapshotUser(models.Model):
    user_address = models.CharField(max_length=100)
    hex_amount = models.DecimalField(max_digits=len(str(2**256)), decimal_places=0, default=0)
    user_hash = models.CharField(max_length=256, null=True, default=None)
    hash_signature = models.CharField(max_length=256, null=True, default=None)
    snapshot_tx = models.CharField(max_length=256, null=True, default=None)
    tx_checked = models.BooleanField(default=False)


class SnapshotUserTestnet(models.Model):
    user_address = models.CharField(max_length=100)
    hex_amount = models.DecimalField(max_digits=len(str(2**256)), decimal_places=0, default=0)
    user_hash = models.CharField(max_length=256, null=True, default=None)
    hash_signature = models.CharField(max_length=256, null=True, default=None)
    snapshot_tx = models.CharField(max_length=256, null=True, default=None)
    tx_checked = models.BooleanField(default=False)


class SnapshotOpenedStake(models.Model):
    address = models.CharField(max_length=512)
    stake_id = models.IntegerField()
    data0 = models.CharField(max_length=512)
    timestamp = models.IntegerField()
    hearts = models.DecimalField(max_digits=len(str(2 ** 256)), decimal_places=0)
    shares = models.DecimalField(max_digits=len(str(2 ** 256)), decimal_places=0)
    days = models.IntegerField()
    is_autostake = models.BooleanField(default=False)
    tx_hash = models.CharField(max_length=512, null=True, default=None)
    block_number = models.IntegerField(null=True, default=None)
    parsed = models.BooleanField(default=False)


class SnapshotStake(models.Model):
    address = models.CharField(max_length=512)
    stake_id = models.IntegerField()
    data0 = models.CharField(max_length=512)
    timestamp = models.IntegerField()
    hearts = models.DecimalField(max_digits=len(str(2 ** 256)), decimal_places=0)
    shares = models.DecimalField(max_digits=len(str(2 ** 256)), decimal_places=0)
    days = models.IntegerField()
    is_autostake = models.BooleanField(default=False)
    tx_hash = models.CharField(max_length=512, null=True, default=None)
    block_number = models.IntegerField(null=True, default=None)
    parsed = models.BooleanField(default=False)
    ended = models.BooleanField(default=False)


class SnapshotAddressHexBalance(models.Model):
    address = models.CharField(max_length=512)
    balance = models.DecimalField(max_digits=len(str(2**256)), decimal_places=0, default=0)


class SnapshotAddressSharesBalance(models.Model):
    address = models.CharField(max_length=512)
    balance = models.DecimalField(max_digits=len(str(2 ** 256)), decimal_places=0, default=0)
    balance_old = models.DecimalField(max_digits=len(str(2**256)), decimal_places=0, default=0)

class SnapshotAddressHex2tBalance(models.Model):
    address = models.CharField(max_length=512)
    balance = models.DecimalField(max_digits=len(str(2**256)), decimal_places=0, default=0)

# class UserBalance(models.Model):
#     address = models.CharField(max_length=512)
#     balance_hex = models.DecimalField(max_digits=len(str(2**256)), decimal_places=0, null=True, default=None)
#     balance_shares = models.DecimalField(max_digits=len(str(2**256)), decimal_places=0, null=True, default=None)
#     token_transfers = models.ForeignKey(TokenTransfer, on_delete=models.SET_NULL, null=True, default=None)
