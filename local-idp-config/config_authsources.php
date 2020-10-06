<?php

$config = array(

    'admin' => array(
        'core:AdminPassword',
    ),

    'example-userpass' => array(
        'exampleauth:UserPass',

        'rmt:' => array(
            'email' => 'rmt@example.com',
            'roleID' => 'RT-HOU1-ZA-01',
        ),

        'hq_fo_ccs:' => array(
            'email' => 'hq_fo_ccs@example.com',
            'roleID' => 'FT-HOU1-ZA-01',
        ),

        'recruit1:' => array(
            'email' => 'recruit1@example.com',
            'roleID' => 'PT-FPR1-ZA-01',
        ),

        'recruit2:' => array(
            'email' => 'recruit2@example.com',
            'roleID' => 'PT-FPP1-ZA-01',
        ),

        'hr:' => array(
            'email' => 'hr@example.com',
            'roleID' => 'PT-FPH1-ZA-01',
        ),

        'fsss1:' => array(
            'email' => 'fsss1@example.com',
            'roleID' => 'ZT-HSA1-ZA-01',
        ),

        'fsss2:' => array(
            'email' => 'fsss2@example.com',
            'roleID' => 'DT-SUP1-ZA-01',
        ),

        'fsss3:' => array(
            'email' => 'fsss3@example.com',
            'roleID' => 'LT-CFS1-ZA-01',
        ),

        'logistics:' => array(
            'email' => 'logistics@example.com',
            'roleID' => 'LT-LOG1-ZA-01',
        ),
    ),

);
