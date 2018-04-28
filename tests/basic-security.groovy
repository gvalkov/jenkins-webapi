#!groovy

// Taken from the excellent Ansible Jenkins role:
// https://github.com/geerlingguy/ansible-role-jenkins/blob/master/templates/basic-security.groovy

import hudson.security.*
import jenkins.model.*

def instance = Jenkins.getInstance()
def hudsonRealm = new HudsonPrivateSecurityRealm(false)
def users = hudsonRealm.getAllUsers()
users_s = users.collect { it.toString() }

// Create the admin user account if it doesn't already exist.
if ("jenkins-webapi" in users_s) {
    println "Admin user already exists - updating password"

    def user = hudson.model.User.get('jenkins');
    def password = hudson.security.HudsonPrivateSecurityRealm.Details.fromPlainPassword('jenkins')
    user.addProperty(password)
    user.save()
}
else {
    println "--> creating local admin user"

    hudsonRealm.createAccount('jenkins', 'jenkins')
    instance.setSecurityRealm(hudsonRealm)

    def strategy = new FullControlOnceLoggedInAuthorizationStrategy()
    instance.setAuthorizationStrategy(strategy)
    instance.save()
}
