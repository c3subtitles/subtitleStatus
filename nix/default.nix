final: prev:

{
  subtitleStatusCfg = final.pkgs.writeText "subtitleStatus.cfg" ''
    [sql]
    type=postgresql
    database=subtitlestatus
    user=subtitlestatus
    password=a_very_secure_password
  '';
}
