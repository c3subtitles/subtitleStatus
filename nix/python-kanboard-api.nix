{ lib, buildPythonPackage, fetchPypi, pyPkgs }:

buildPythonPackage rec {
  pname = "python-kanboard-api";
  version = "1.1.3";
  meta = {
    description = "Client library for Kanboard";
    license = lib.licenses.mit;
    homepage = "https://github.com/kanboard/python-api-client";
  };

  src = fetchPypi {
    pname = "kanboard";
    inherit version;
    sha256 = "sha256-iYNRm/puHPx/66D+DmNaq4WviLZmfOb04bsspaocOh4=";
  };

  buildInputs = with pyPkgs; [ django six ];
  propagatedBuildInputs = with pyPkgs; [ django six ];
  doCheck = false;
}
