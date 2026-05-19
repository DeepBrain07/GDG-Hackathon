from apps.core.services.notification_service import NotificationService

class NotifyServices:
    """
    Initiate → Pay → Webhook → Verify → Wallet  FUNDED
    """

    @staticmethod
    def payment_success(transaction):

        offer = transaction.offer

        NotificationService.create(
            user=offer.sender,
            type="payment_success",
            title="Payment Successful",
            message=f"Your wallet has been funded with (amount: {transaction.amount})",
            content_object=offer)
