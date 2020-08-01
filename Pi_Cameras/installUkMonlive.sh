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
� )d$_ �:l�u�wM)�$�c�"���b[��ǯ$�2)��dS+RE��].��xk��v�$Ғ"YN�p!�V�u*��(TI�F@��i��0\TH�6���t�줵���bߛ���[Q7���7��̛y��{of޼�e^ߣm3��m�q+G�IJB����2�ӕ������Iu���==�퀗Juu���6�Ԧ�e�&���_�J��G���e�LL�ńV�C'T+
��#�^�i�R'���sMh_�B��9�ʬm�׬��X���/r�ȡ��cH ӮR�P3�6ذt�6a�6�ǚ�|��V��9ݢ*��6���Ьg��uZ,�(�e�Km���G ��iE�_�T�z^�g�F�٢Z�@K��;���Pbhg��!��3�㌞��hi����DTp��#w��P�7&'5��c(m���bҘM�IA��Dyw�(&�
�&��K�d���!�U
��&U�Z4�Z3iya(�t��t�G7�j����&�koN��Mw2`4�Y��W�y�x�?l�����M�F����׋5J�n����M]J���R�1c0yӪ��h��E)�}?�ŪJ���;��Js�t��.�c+&iMŻ�>:�c���%K*�ӕiS��QF��f���h4����Y���Y;�1�Zgqؘt�6�m��I+t%%�����R�5ܵjQNƷ,��o��3D~�������ò��(�C.pRܵt�Qdy����� �t�"M��liZ�wĎ�l��*�V�a��]q��ٷU=HP�i�Gc)t"|�����:D�����uQ?��|ge�VG^��sn�rf5.�s����ȀM����#+�i%ڑL�oS�ӚPj��䢀rC7��Դ��o��f�zD�Q�IX�b�6����Zb{���&e��FO2�׻r_%��U��Oս���J,N�v �.�����VL�]65
�K�0�Q��S���д"nA��Ϭ,���:��\�Ͱ\��)k��> Nﴍ򽷈���eǙ�+|�@����=U�s0�˾�ˏY{V0
1VՎ�x�?b��	F)�/��^Ќ�ۖ-"��Y�k�e�-;��r��
���D�闒|1�5�
��Twg7������I~������>��?��ٽ�2�&�KNxǵ�6����쁓��p��Q��
���,U��B�n����'Q,Clپ��T�a��A�'qW��9%�Hk���
�n*J�0Z����,'!�a�z?`ة[�����0V��*|��]�J�v<#ĩ�l=o�7�v:74d[�ը�hiRлr���p�A�����}h�dA`bj�L�g�7v�Ղs]��#^:����?�>�ؗ��ٗ��綄S� �p�؅дY%��t*�c���X7�0�HOOl�x(W�f<�@HO�ci���qB�&�PQۛ��ݗ�(�}v�F��@���i݇�FЪ`J۝�P�Ìħ
yqߔ�ă��;�}����Vbێ�c[т������4V���X9��lݾkl�t�FQK�����	+Ҭ� VbR�5�]�B>�"R�Bl�Aq!{Ć�	Ný���)q�5<��ֻVc����켤����@���Nuvwu���o������=��ۣ�\�z�T<)S��60p�w�����ލ�{�YCD�
�Ɇ�q��S]2��q��p��~�i�W��&�\��;���m3�Z�2�1�:��iք8Z�a�<>��>��6���d���?<�h�A�r;���)��T���-i�������S{W���r���ZF�f��K��5KLY@�L^��+w""o�Q�:pg Sc��LP�@��؊����Z��>0+�BA+�X��f�մ�T���2E2�Qb�#����^{�T;�:D7��Y;�������Oi�%�/�h��2��c}W���S���80�'!x\5����݂eG�[�\O]�e�b��n�'lz�4�S���"� �L�3q���X��\M��s&�������S=�ݝ���{:{R)�'�R�u��I����C�$U� �� �Z�D:�|�fhk K`:H��Jڰ��!l�C˭���A�Fȝ,K,3����� �I�%�a�HU$�6���6l�m��A�=��m�`���\��#f��� o���J��,f+�CN���D>�Y�<S�B.��x�a!�}�w	�rZ*�#�����x�ɜ���������7����ՠ�w��ÁuR�m/`�Z�������ٶ��˚o�Ɵm�������7���g��{���~���r|�{o�+ o��o��_�������~����-��>��L�ӊ��Oe��6%W�I݂vl�@�(jc�D^#�2	.Nao]�B���(;�@^�,��� V5uBW�Žz1��K%�d�p�4��M,�L��	^:�����T�-�N�����V�4�!����Er�����"�o�4���;��A�����VX�îۧ�����"������ �Q(?)�%,�;�̵XBKXl�X^G�:,�`�a���>,a䦾�;	B~�t��ن�X�a�X���#�M���r�:��{G�ï>5⃗+N������>�?�?��?��ԧ�~|�4��9��ʙetf���<$V	�r���J��B�UZ��*?\X��9ȯ���,��e�#�X%�<2���;!;Oz!!���»6JϢ6�i#�3>�HF��w��Fx]Z����������c�(�K�����3s/��������O7��M[��?��'|�d+�,%A��w* �E\�=�'ɧX�����ggAf���B��<��fΟl���p�w�ç�͇Is%n3����l��ϻa�
쵪��@�	��ó$�/��̍�~A���l�'%��GH�:�U���� �';��.,�v�7��{sU�q�M���é�ɓ'Ϟ��qd� 3�����ݨO�0�;�a��A�}=��ڛX�I�#~ u8)��/"�"/"�~V򽷃�3s}��ØX����
u�P�&a3�~��_lr��~���E�G7������a��ϊ�J��\9|��3���gNh��ȊU�8/f��hٵ��[�o�q��3�A�����$QyK�~��p�h���6����
�t��W�8?r�z�yim_U�9�9	$W���@��	�I�J �_���ƅ�eFP�`xf��Ⱦ� �|�7W$!��$���� �8D]=��y*Y�v��)�9��2s���I��O̓��q��_�W������tl�4�f ��(�3�^|8ny�>0��9�-0珂����X��.7�|X̅�߄ ��@�R��?V9Vi?2�d��l�6+��<=3��!����'N65�Γ���R���ߨ\��`��0������ �٧��{2��9�x.aD��d������C����}��{� ����O:�[�0���H��I��nƳ�>���$o�x��q�*��[� �M��ua�8
q&Ư'��^c�7!7���F��i�����E��&������ 8��JQ^XX0�C��Hg��LЍ��6E�s�0�y��M�l�w�T�҄�ig|}�=�J~6�M�+���c��w�Rkx���a��."��%ݤ��IZ*�+VJ�F�`�t�tK`U�M�%���:�m�2��؋K�ċ����7m��꤀&���DY�H^��T+G��"��m���U(�gjy��R��!����f�.�����wn�C3Jūzf�ĵ���~8����:�)���i�	��4` c�p²H\�.q��m��Dن�v��)�zAq���|�KU�G�G�p+_���6�����嬷 ���ǫp+�Uᥬ<_��{M_�7W��[X�Z^�J����g�0���<"��
/ge�ف٭��c�de[���Va�[�U�S�_����-U���#U�f�MA�5��*��Y�'�w�0���{���=�}�g��70ؑo�#������=p@��z���:^3�ߪ�w=yq�[|����|�?'��%�?����׍�>�F|�=��$v�\Rk�a�}����?!��C��?(���g�ͬ���[#dLra��0�/{��I.����O��*��䋒K 3����L^�,(g=����g>��X74���_���B��*&��m��P�|�����#UyV���\OG��y`���T�~����w~V�w%wK��*�ڻ1��w	�;�랇-l��=0��{� ׯ�I���u�]v��p�'��7p�3�Bu��k�[�p��
�O�>��������>�������g|��M�?��3>�p���@��Q��?B������ן
��������>�
��7t�#���&��,�#>�/k��' ��@X�� �%����g�<�~����@�3ാ#��6�үip��
<ٟ����d:�P͂x�����\6�U"�CH�v*n�h�DՏ����j>�����J���p-"WӶ�r6OE�`�2�utLQ��̧�%�ouY�IQ2�2�7&Լ����_���p���l-_�Lv.���ї��9MX��dʅ�4�x ����A%�.�����#n�����m�������Tr�5\2D�����m[j{س!Q�ޱ�X�144:8���oT��ŴUf�_�A�G��1��4� ��U��������w�����C��m�}�ƿ�I��4�1�5���Z�Y�X�d,Cɩ�ȍo�5�[w bF/*eKˈ��EFB���|��\��������a��z�is�d��ha*׆���A�1��.� �<:���Z�a��Eq�7�z6kA�Ks��U'����AOſɐ���9�VC�N��o'܏9�q_)�'Jx�.���\�wU�g�x�f���,����u��%�ۈD�o.�J��xx/9��k��ٹ#�}� j�y7�wj��=�8���ی��c���6�ߜ���W��x������=�x���8���������<~'��3<<_��p������a��V��[[-�w���}&��|/z�0<w	��q��a�|S�����^���8/���y�G��Z����>������\�b\����^�4�C<�������=���c��/�����a[Z��_���j�s�����|WG��><�x ^%��h��~~�IMHG�x7J�9s椷`bO���4�"��]���U�E>�KV=�S=�S=�S=�S=�S=�S=�S=�S=�S=�����?�+z P  