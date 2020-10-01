<?php

$config = array(

    'admin' => array(
        'core:AdminPassword',
    ),

    'example-userpass' => array(
        'exampleauth:UserPass',
        'user1:user1pass' => array(
            'email' => 'user1@example.com',
            'roleID' => 'Foo',
        ),
        'user2:user2pass' => array(
            'email' => 'user2@example.com',
            'roleID' => 'Foo',
        ),
    ),

);
