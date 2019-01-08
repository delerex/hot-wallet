const baseUrl = "/api/";

const API = {
    login: "login/",
    wallets: "wallets/",
    mnemonics: "mnemonic/",
    networkType: "network/type/",
    assets: "assets/",
};


function GetAPI(endpoint, data, callback) {
    var xhr = new XMLHttpRequest();
    var params = "";
    Object.keys(data).forEach(function (x) {
        if (params == "") {
            params += "?" + encodeURIComponent(x) + "=" + encodeURIComponent(data[x])
        } else {
            params += "&" + encodeURIComponent(x) + "=" + encodeURIComponent(data[x])
        }
    });


    xhr.onreadystatechange = function () {
        if (xhr.readyState != 4) return;
        //       alert(xhr.responseText)
        if (xhr.status == 200 || xhr.status == 500) {
            if (callback) {
                callback(JSON.parse(xhr.responseText));
            }
        }
    };


    xhr.open('GET', baseUrl + endpoint + params, true);
    xhr.setRequestHeader('Content-type', 'application/json; charset=utf-8');
    xhr.send();

}

function PostAPI(endpoint, data, callback) {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (xhr.readyState != 4) return;
        //       alert(xhr.responseText)
        if (xhr.status == 200 || xhr.status == 500) {
            if (callback) {
                callback(JSON.parse(xhr.responseText));
            }
        }
    };

    xhr.open('POST', baseUrl + endpoint, true);
    xhr.setRequestHeader('Content-type', 'application/json; charset=utf-8');
    xhr.timeout = 30000;
    xhr.send(JSON.stringify(data));

}

function PutAPI(endpoint, data, callback) {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (xhr.readyState != 4) return;
        //       alert(xhr.responseText)
        if (xhr.status == 200 || xhr.status == 500) {
            if (callback) {
                callback(JSON.parse(xhr.responseText));
            }
        }
    };

    xhr.open('PUT', baseUrl + endpoint, true);
    xhr.setRequestHeader('Content-type', 'application/json; charset=utf-8');
    xhr.timeout = 30000;
    xhr.send(JSON.stringify(data));

}


function APILogin(user, password, callback = null) {
    PostAPI(API.login, {user: user, password: password}, function (response) {
        if (callback) {
            callback(response);
        }
    });
}


function APIGetMnemonic(callback = null) {
    GetAPI(API.mnemonics, {}, function (response) {
        if (callback) {
            callback(response);
        }
    });
}

function APIAddWallet(wallet, mnemonic, password, wallettype, networkType, callback = null) {
    PostAPI(API.wallets + wallet + "/", {
        mnemonic: mnemonic,
        keypassword: password,
        wallettype: wallettype,
        network_type: networkType
    }, function (response) {
        if (callback) {
            callback(response);
        }
    });
}

function APISetOuts(wallet, currency, password, outs, callback = null) {
    PostAPI(API.wallets + wallet + "/" + currency + "/outs/", {password: password, outs: outs}, function (response) {
        if (callback) {
            callback(response);
        }
    });
}


function APIGetWallets(callback = null) {
    GetAPI(API.wallets, {}, function (response) {
        if (callback) {
            callback(response);
        }
    });
}

function APIGetWallet(wallet, callback = null) {
    GetAPI(API.wallets + wallet + "/", {}, function (response) {
        if (callback) {
            callback(response);
        }
    });
}

function APIGetAddress(wallet, currency, number, callback = null) {
    GetAPI(API.wallets + wallet + "/" + currency + "/" + number.toString() + "/address/", {}, function (response) {
        if (callback) {
            callback(response);
        }
    });
}

function APIGetFeeWalletAddress(wallet, currency, callback = null) {
    GetAPI(API.wallets + wallet + "/" + currency + "/fee/address/", {}, function (response) {
        if (callback) {
            callback(response);
        }
    });
}

function APIGetBalance(wallet, currency, number, callback = null) {
    GetAPI(API.wallets + wallet + "/" + currency + "/" + number.toString() + "/balance/", {}, function (response) {
        if (callback) {
            callback(response);
        }
    });
}

function APIGetFeeWalletBalance(wallet, currency, callback = null) {
    GetAPI(API.wallets + wallet + "/" + currency + "/fee/balance/", {}, function (response) {
        if (callback) {
            callback(response);
        }
    });
}

function APIGetNetworkType(callback = null) {
    GetAPI(API.networkType, {}, function (response) {
        if (callback) {
            callback(response);
        }
    });
}

function APIPutNetworkType(network_type, callback = null) {
    PutAPI(API.networkType, {network_type: network_type},
        function (response) {
            if (callback) {
                callback(response);
            }
        });
}

function APIGetAssets(callback = null) {
    GetAPI(API.assets, {}, function (response) {
        if (callback) {
            callback(response);
        }
    });
}

function APIPostAsset(symbol, contract_address, coin_index, decimals, password, callback = null) {
    data = {
        asset: {
            symbol: symbol,
            contract_address: contract_address,
            coin_index: coin_index,
            decimals: decimals,
        },
        password: password,
    };
    PostAPI(API.assets, data, function (response) {
        if (callback) {
            callback(response);
        }
    });
}

function APISendTransactions(wallet, currency, start, end, password, callback = null) {
    PostAPI(API.wallets + wallet + "/" + currency + "/transactions/", {password: password, start: start, end: end}, function (response) {
        if (callback) {
            callback(response);
        }
    });
}
