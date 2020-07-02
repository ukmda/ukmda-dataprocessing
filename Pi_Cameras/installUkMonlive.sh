#!/bin/bash

echo "This script will install the UKMON LIVE software on your Pi."
echo " "
echo "You will need the location code you agreed with UKMON, "
echo "and the access key and secret provided by UKMON."
echo "if you already contribute from a PC these can be found in"
if [ "LIVE" == "ARCHIVE" ] ; then 
  echo "%LOCALAPPDATA%\ukmon\ukmonarchiver.ini. "
else
  echo "%LOCALAPPDATA%\AUTH_ukmonlivewatcher.ini. "
  echo "The short string is the Key and the long one the Secret."
fi
echo "Please enter the (encrypted) values exactly as seen"
echo ""
echo "If you don't have these keys press crtl-c and come back after getting them".
echo "nb: its best to copy/paste the keys from email to avoid typos."
echo " " 

read -p "continue? " yn
if [ $yn == "n" ] ; then
  exit 0
fi

echo "Installing the AWS CLI...."
sudo apt-get install -y awscli

mkdir ~/ukmon
echo "Installing the package...."
ARCHIVE=`awk '/^__ARCHIVE_BELOW__/ {print NR + 1; exit 0; }' $0`
tail -n+$ARCHIVE $0 | tar xzv -C ~/ukmon

CREDFILE=~/ukmon/.livecreds

if [ -f $CREDFILE ] ; then
  read -p "Credentials already exist; overwrite? (yn) " yn
  if [[ "$yn" == "y" || "$yn" == "Y" ]] ; then 
    redocreds=1
  else
    redocreds=0
  fi
else
  redocreds=1
fi

if [ $redocreds -eq 1 ] ; then 
  while true; do
    read -p "Location: " loc
    read -p "Access Key: " key
    read -p "Secret: " sec 
    echo "you entered: "
    echo $loc
    echo $key
    echo $sec
    read -p " is this correct? (yn) " yn
    if [[ "$yn" == "y" || "$yn" == "Y" ]] ; then 
      break 
    fi
  done 
    
  echo "Creating credentials...."
  echo "export AWS_ACCESS_KEY_ID=`/home/pi/ukmon/.ukmondec $key k`" > $CREDFILE
  echo "export AWS_SECRET_ACCESS_KEY=`/home/pi/ukmon/.ukmondec $sec s`" >> $CREDFILE
  if [ "LIVE" == "ARCHIVE" ] ; then 
    echo "export AWS_DEFAULT_REGION=eu-west-2" >> $CREDFILE
  else
    echo "export AWS_DEFAULT_REGION=eu-west-1" >> $CREDFILE
  fi
  echo "export loc=$loc" >> $CREDFILE
  chmod 0600 $CREDFILE
fi 
if [ "LIVE" == "ARCHIVE" ] ; then 
  crontab -l | grep archToUkMon.sh
  if [ $? == 1 ] ; then
    crontab -l > /tmp/tmpct
    echo "Scheduling job..."
    echo "0 11 * * * /home/pi/ukmon/archToUkMon.sh >> /home/pi/ukmon/archiver.log 2>&1" >> /tmp/tmpct
    crontab /tmp/tmpct
    \rm -f /tmp/tmpct
  fi 
  echo "archToUkMon will run at 11am each day"
else
  crontab -l | grep liveMonitor.sh > /dev/null
  if [ $? == 1 ] ; then
    echo "Scheduling job..."
    crontab -l > /tmp/tmpct
    echo "@reboot sleep 3600 && /home/pi/ukmon/liveMonitor.sh >> /home/pi/ukmon/monitor.log 2>&1" >> /tmp/tmpct
    crontab /tmp/tmpct
    \rm -f /tmp/tmpct
  fi 
  echo "liveMonitor will start after next reboot"
fi
echo ""
echo "done"
exit 0

__ARCHIVE_BELOW__
� ��^ �Yl�u��;Qԑ�O�9�-"��.���~�';�E��~lRbE��]����כּ���DZ�%�i�*��j�NE��� UҦ�u�$-��#!)�+;i� ���������Nv�F�ܐs3o�7o޼�y���>uL+�LM�YrCBB_O�ɾ��;ŐL%{I�����+�4I$�=�^B7F��P6LY���r��0��Ӱ���\1>-�`p��5�*�56A��� ����6sZ1%����A�IS�O�%)�)ǁa��=1��85�\@�˪���`Z.)9�jFWKT�Zh��s"��h������Jz�h�H���SA5��h:����3���z{������*ձ�|���OSE�bJ�1��"`�蕦���S��D�Q�>�Y�\��*�l��4A���U�,C��=a�3��\P��~:�<�k�JŌV.*T�\��fb���匪8�xyoA+���v�򚬨�h�w:nU`�L�%�,����f:�������+�a�@�z )Z�\Tgs��
��W�/^��i���o������d���?lM��Q��7���Vk�?�s#����p���gd��ɦ��S��R��Y(�h\Q�ŋ�|���3ܣh4����	�e��Q�A�B#�Id`{u�ZA������E����U��+��Q�4gf�"��n3�7b���l�bj��Z�壥�`I+)51��utF5)ll*��[�9PfJ�d�v��A��l���@����>W��{D)#]6iT��$�RSAż>�k*h~@�nk7g\ >lf!8��*�v�t2
؂ր���p����ٚ4���zr8]؎�6�v�Eu�,r@1J�f�Z���`a�g� ��-���3j���q��� �P�F���]�ȁ9�`��F|l��m�HACbx��xD��춝���f��ݓ# �!512�*fG��a�N�b̃Z��{�Z�����ߠFř�R���*Q\;�kq���~���ۺ7�t�������ޞ$����Kt��Ou������o��O�8����XB�j1�)p&�wOn�n����3��̲�Jp��tũ�J��t�_�5)Rp9"[�"U�EX�"�����,�Ej�Ej�9h()ҌJ{��<6>�c+�dr��"����u�A�r
�Nu�4=�/���$Z�����HJ��`v����/vA=4�)9�g��+i�*��c*��Q��~���Z��@
8�jӆ�C��E��X�^���j�@�%Z��M���]��rZe]��ΰ�(�Vb�G
l����(c~HQ�7H>�>�%�R��l�w�%��)�%=�����(¡��-� �h�� �J@ ݐ�q��2�
�;H'�K�Ä|?(��8�+�@�fQ`�	������'`X�&X��
��h#,.�ʰ���X���]���7҆���e�/[z�:���v�~�b*�l��C�f<�+�y˳QY/d31C�u�~��|�ݖMy]j�Ö����T�U�|�����=���_��E����=����'^�<��vl���?��g;g��l��+���{�������=�����W��]y��S�}�[�>�����C����=}�C����-��.��3�d��D�>9&�V���a'ǆ�ZQ����*��pq�sS����>i���ˆ���u*˪<�������"�K%��'��4��KSO��>c���dH�lD��tٰ��Z0T�aEK���+��CCRW��lݾyHJź�>�ٯ���g?έ�5��kC�?Z��{��c�r+Q�y�n��[@��c0�"��ĺS@n��	La�uc�������:�t!�B˭ѷ�|���K��h%�p�r�±���S9�4�ֱ���G�μw�b�O��\�yW�9W��+��+ؕ�����da�B �+��b��>$Z	�t�x)Zi''+퉓��V�߻�U�]�
�����<LOV��c>�����ǫq�ߪշ�o�E���$��Zh!������T�`��v�u$t���Z\5���O.|=tz��z�z!�i� ���0���:Pg!�K|��%Ģ�Q>Ig8�����.-�ζ�W��.��h�O�E�
��������i��Cm c�Bk�����y;Dׂ��V��#aȷb>qd�$��"���)������SK(�� �r�dm�(�	�X}�k�R���5�(�B���C�k+O"61�����-���]��c�LAg
:G���G��ۺ!�.c��^����1ߗZB��t¢�.\�-\�����;o�S�}�ͰMC��v ����yp��V�f���~����}�G؏6��~��~�0�>���J��V9��%߆��%�����X�tx���\��*������-��>�$�����sd~�$PqSw���a����כ8/|k+��Ї]ut^��#�������P7���/������C�,� zy��n�]�Vg�������� gU[E�t��@��V��ӏ��v�&���AY(	6�k�eB�/|��I��SK$�l����_�d��$���^�m�uV�!��@���j�e�öp�Q���f��a��>�Y��F�U�7�|��-�
�+CѷHi~qt�det�d�e��²�c-S�px~�w|~1u�ȧ�<u�50>�D�/�Y
$�RY�Z��0��Z���{��퀽t���!�_]D����?�H�
���?�<}��g0����p/��Z=>�P��ig�	��2��S��{+���|�%y#�ϯx]K���v�+�����Z�N�9ϯg|;ӽ
4��^��f�׷���p;��~^��Gn�x�/��eH�[2Yc�W�U�4�W!ź��i�����O"�>a��a��<s�k�l��sr�v���ħuzc9u7/��1�M��3d7[v�"�]�KZZZ�Bз:�F���;�ۄ�}k���(��1W0�iHM��Y;�n�%+j�ܼ=j�35S,Ǧ�98��¨�ldIL�+�<��:�X�u�<]�#�gJy��`�Tg�7�4�@Jb���bP�Z�lN�%15+��?�)ɺ.��v�ѴΔ��4(��`.p�0H�z]�2e��s�eδ�C�u��[����ǼT��	�D�����oc8�9�o_�|��,=]�[Yz�F�`��_86�V��ng�+5z%Kq�q�&�^����s�F���5zK�m6�nlszK;kt���F�������m�V�n��,�ѷw�3�����
�T$�x�~�e�x��?����/��73��o���P~�2���h�%/��#~��^�ߨ�wy���m�����c��_ �#~��}�nl��7��o�����?���^�.�`�.~\ph��D���������[�dRph��0�g]�m���G����5䳂C@��������P�|�����<������9��<�R���\�C�/=�c}Ӄ?��W]�w> >\�g5�[��qwD~���埄��C<�^�㳆�-8�[���C���->g���Q_g?lg��q�ȟrѝ>޿ �~%��l��n���O
�o��g�S�줋���;��s��jXOs�o��C��yO|KC}���>������G�������a?j��!?�G��U0����~>?�>���}�f������>�*��}̃���޾4��,{�����WV��������G�%�<��z���ാa���׿;���ո�ˆ�g�鸬�H8��a)����*�Y�� i�L�4QHD�وˁ����K�Uy��)�l�Q�nf9����$=8�K�>1)I�y�̂�Ʒ:�4(�$E�f�ڴ��S�I.�8.��*�{��� �9}Ip���;�IJ�P��*.Jrm���K�JD�g���iPoˮ��id�0>C�.��:)
���18�}��Þ��ut���Qi�-#�������~YLe��>����&��yE�Ǭʎ��0��w8��#��6u65G���xz�q����ux�#h=���VRM��E��7�:��� TrE�l����ڠ%4
;�7~̅�#,����Fò�#}#Ŵ>W2��h�T�	{�E�pc��.� ����z�a��Iq�7�G��U�"쥹N��O�ފ^=�&C�N�����rǿ�p?f�}%]8�O�pm��o.�ZwU�g�x�2#~{h�����U�-�mD �7�_&|�A�K�����ۏ_�hߑ��T�t���^��Ԙ�{�i��یݏ� ����~s�����~ ����L��犟������t�v���u����g]8~'�����W�0�r���\8<7�$֭��Gę/�_6��Eρ����Ǖ���"���҃;뒇�p��s�E��\���M�w1ı����c��8<?���.n;��o��wG����K����{�[��px���x<޳�"�G��Ϟ��[y��:�=8�x Y%��D;_�^y�Hݑ�|p����1��0���A|�g�����"�㮎��/Y�������������������������������� 
h:� P  