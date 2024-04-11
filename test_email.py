import pytest
from emailSender import envoyer_email
def test_envoyer_email():
    # Tester l'envoi d'un email
    destinataire = "destinataire@exemple.com"
    sujet = "Test d'envoi d'email"
    corps = "Ceci est un email de test."
    result = envoyer_email(destinataire, sujet, corps)
    assert result
def test_email():
    pytest.main(["-v", "test_email.py"])