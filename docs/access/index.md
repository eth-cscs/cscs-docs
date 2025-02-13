# Connecting to Alps

This documentation guides users through the process of accessing CSCS systems and services.

!!! info
    Before accessing CSCS, you need to have an account at CSCS, and be part of a project that has been allocated resources.
    More information on how to get an account is available in [accounts and projects][account-management].


There are different ways to authenticate your identity in order to access services at CSCS, using a password set by the user. Currently users can be authenticated with:

* Classic ssh with CSCS username/password, and also with ssh-keys
* CSCS username/password on different web services. Sessions can be independent from each other so, signing into one service does not necessarily sign the user into another one
* CSCS username/password on a Single Sign-On gate, which once the user is authenticated, can move between services (connected to this gate) without signing in again
* Username/password from an external institution, provided that his/her CSCS account has been "linked" to that external identity beforehand and the service uses the Single Sign-On gate

## Single Sign-On

Most services at CSCS are connected to the CSCS Single Sign-On gate.
This gives users the comfort of not having to sign in multiple times in each individual service connected to this gate and increases security.
Furthermore, the Single Sign-On gate allow users to recover their forgotten passwords and authenticate using a third-party account. The login page looks like
