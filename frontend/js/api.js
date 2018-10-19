const baseUrl = "http://127.0.0.1:3200/";

const API = {
    login:  "login/",
    wallets:  "wallets/",
    mnemonics: "mnemonic/",
};




function GetAPI(endpoint, data, callback) {
    var xhr = new XMLHttpRequest();
    var params = ""
    Object.keys(data).forEach(function (x) {
        if (params == "") {
            params += "?" + encodeURIComponent(x) + "=" + encodeURIComponent(data[x])
        } else {
            params += "&" + encodeURIComponent(x) + "=" + encodeURIComponent(data[x])
        }
    })


    xhr.onreadystatechange = function () {
        if (xhr.readyState != 4) return;
        //       alert(xhr.responseText)
        if (xhr.status == 200 || xhr.status == 500) {
            if(callback){
                callback(JSON.parse(xhr.responseText));
            }
        }
    }


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
            if(callback){
                callback(JSON.parse(xhr.responseText));
            }
        }
    }

    xhr.open('POST', baseUrl + endpoint, true);
    xhr.setRequestHeader('Content-type', 'application/json; charset=utf-8');
    xhr.timeout = 30000;
    xhr.send(JSON.stringify(data));

}


function APILogin(user, password, callback=null){
    PostAPI(API.login, { user: user, password: password }, function (response) {
        if(callback){callback(response);}
    });
}


function APIGetMnemonic(callback=null){
    GetAPI(API.mnemonics, { }, function (response) {
        if(callback){callback(response);}
    });
}

function APIAddWallet(wallet, mnemonic, password, callback=null){
    PostAPI(API.wallets+wallet+"/", {mnemonic : mnemonic, keypassword : password }, function (response) {
        if(callback){callback(response);}
    });
}

function APISetOuts(wallet, currency, password, outs, callback=null){
    PostAPI(API.wallets+wallet+"/" + currency + "/outs/", {password : password, outs : outs }, function (response) {
        if(callback){callback(response);}
    });
}


function APIGetWallets(callback=null){
    GetAPI(API.wallets, {}, function (response) {
        if(callback){callback(response);}
    });
}

function APIGetWallet(wallet, callback=null){
    GetAPI(API.wallets+wallet + "/", {}, function (response) {
        if(callback){callback(response);}
    });
}
function APIGetAddress(wallet, currency, number, callback=null){
    GetAPI(API.wallets+wallet + "/" + currency + "/" + number.toString() + "/address/", {}, function (response) {
        if(callback){callback(response);}
    });
}

function APIGetBalance(wallet, currency, number, callback=null){
    GetAPI(API.wallets+wallet + "/" + currency + "/" + number.toString() + "/balance/", {}, function (response) {
        if(callback){callback(response);}
    });
}
