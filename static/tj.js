// 参数： eventName [, options]
// eventName
// options

// ['eventName',...]

(function (root) {
    'use strict';
     // 设置cookie
    function __setCookie(name, value) {
        var days = 1
        var exp = new Date()
        exp.setTime(exp.getTime() + days * 24 * 60 * 60 * 1000);
        document.cookie = name + "=" + escape(value) + ";path=/;expires=" + exp.toGMTString();
    }

    // 获取cookie
    function __getCookie(name) {
        var arr = document.cookie.match(new RegExp("(^| )" + name + "=([^;]*)(;|$)"));
        return unescape(arr[2]);
    }

    // ajax请求
    // url 链接
    // type 请求类型
    // data 请求数据
    // successCall 成功回调
    // errCall 失败回调
    function __ajax(conf){
        var {url,type,data,successCall,errCall} = conf
        var xhr=new XMLHttpRequest();
        xhr.open(type,url,true);
        // xhr.withCredentials = true;
        if(typeof data === 'object'){
            xhr.setRequestHeader('Content-Type','application/json')
            data = JSON.stringify(data)
        }else {
            xhr.setRequestHeader('Content-Type','application/x-www-form-urlencoded')
        }
        xhr.onreadystatechange=function(){
            if(xhr.readyState==4){
                if (xhr.status>=200&&xhr.status<300||xhr.status==304) {
                    successCall&&successCall(xhr.responseText)
                }else{
                    errCall&&errCall(xhr.responseText)
                }
            }
        }
        xhr.send(data);
    }

    // 生成唯一标识
    function __uuid() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            var r = Math.random()*16|0, v = c == 'x' ? r : (r&0x3|0x8);
            return v.toString(16);
        });
    }

    function getUUID() {
        var uuid
        try {
            uuid = __getCookie('gemii_uuid')
        } catch (error) {
            uuid = __uuid()
            __setCookie('gemii_uuid',uuid)
        }
        return uuid
    }

    // loading event
    // http://tj.dev.gemii.cc:58080/e/?_s=SITE&_p=URL&_u=UUID&_e=EVENT&_a0=ARG0&_a1=ARG1

    // laodng
    function __loading(){
        var __pathname = location.pathname
        var url = `${__host}/e/?_s=${__site}&_p=${__pathname}&_u=${__uuid}&_e=__LOADING__`
        __ajax({
            url: url,
            type:'get',
            data: null
        })
    }

    // 事件
    function __push() {
        var ar = arguments
        var __pathname = location.pathname
        var __event = ar[0]
        var url = `${__host}/e/?_s=${__site}&_p=${__pathname}&_u=${__uuid}&_e=${__event}`
        if(ar.length>1){
            for(var i=1;i<ar.length;i++){
                url = `${url}&_a${i}=${ar[i]}`
            }
        }
        __ajax({
            url: url,
            type:'get',
            data: null
        })
    }

    function SDK(env,site) {
        this.host = env.toLowerCase() == 'prod' ? 'https://tj.gemii.cc' : env.toLowerCase() == 'test' ? 'http://tj.test.gemii.cc:58080' : 'http://tj.dev.gemii.cc:58080';
        this.site = site
        this.uuid = getUUID()
    }

    SDK.prototype.loading = function() {
        // loading
        var ar = arguments
        var __pathname = location.href
        var url = `${this.host}/e/?_s=${this.site}&_p=${encodeURIComponent(__pathname)}&_u=${this.uuid}&_e=__LOADING__`
        for(var i=0;i<ar.length;i++){
            url = url +'&_a'+(i+1)+'='+ar[i]
        }
        __ajax({
            url: url,
            type:'get',
            data: null
        })
    }

    SDK.prototype.loaded = function() {
        // loading
        var ar = arguments
        var __pathname = location.href
        var url = `${this.host}/e/?_s=${this.site}&_p=${encodeURIComponent(__pathname)}&_u=${this.uuid}&_e=__LOADED__`
        for(var i=0;i<ar.length;i++){
            url = url +'&_a'+(i+1)+'='+ar[i]
        }
        __ajax({
            url: url,
            type:'get',
            data: null
        })
    }

    SDK.prototype.push = function () {
        var ar = arguments
        var __pathname = location.href
        var __event = ar[0]
        var url = `${this.host}/e/?_s=${this.site}&_p=${encodeURIComponent(__pathname)}&_u=${this.uuid}&_e=${__event}`
        if(ar.length>1){
            for(var i=1;i<ar.length;i++){
                url = `${url}&_a${i}=${ar[i]}`
            }
        }
        __ajax({
            url: url,
            type:'get',
            data: null
        })
    }


    root.SDK = SDK
})(window)