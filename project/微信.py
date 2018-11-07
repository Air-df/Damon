import requests


headers_str = """"""
headers = {x.split(':', 1)[0]: x.split(':', 1)[1] for x in headers_str.split('\n')}
url = 'https://mp.weixin.qq.com/s?__biz=MjM5MDYwNDMyMQ==&mid=2651743015&idx=3&sn=88300361c8ef15affd8e5b3963f08080&chksm=bdb88e698acf077f696c79bd43099d96a3c5e4146c62e9c93fb4bb2cf53ce3a2c1220e71d477&key=92d0511f99ff2b3e7e219ffede159020535e3d691cc8e38961ab17f7cc7dc2f56adaee17cf3b61877505ef8bb9bc86a25830b89d0da349d423da70ddd6da3eb1109f9075702d73a73bde6d3c9561468d&ascene=0&uin=MTE1MjQxNTE1&devicetype=Windows+7&version=62060426&lang=zh_CN&pass_ticket=JUWLPXShnHcrqGHVkyTThY3jfycZe5Cke%2BJcHHgegVg%3D&winzoom=1 HTTP/1.1'
res = requests.get(url, headers=headers)
html = res.text
print(html)




"""
var new_appmsg = 1;
    var item_show_type = "0";
    var can_see_complaint = "1";
    var not_in_mm_css = "//res.wx.qq.com/mmbizwap/zh_CN/htmledition/style/page/appmsg_new/not_in_mm3ec991.css";
    var windowwx_css = "//res.wx.qq.com/mmbizwap/zh_CN/htmledition/style/page/appmsg_new/winwx3ec991.css";
    var article_improve_combo_css = "//res.wx.qq.com/mmbizwap/zh_CN/htmledition/style/page/appmsg_new/combo417d8e.css";
    var tid = "";
    var aid = "";
    var clientversion = "16070322";
    var appuin = "MjM5MTA4Mzc2MQ=="||"";

    var source = "4";
    var ascene = "0";
    var subscene = "";
    var sessionid = "";
    var abtest_cookie = "BQABAAgACgALABMAFAAFAJ2GHgAllx4AWZkeAIWZHgCNmR4AAAA=";

    var scene = 75;

    var itemidx = "";
    var appmsg_token   = "980_hmVbpDRN2ZxchWMIG6on1cBfLEYHP8387gaYnA9WiEpZqq1_3QjX2cbtzbU~";
    var _copyright_stat = "0";
    var _ori_article_type = "";
(function() {
	    var params = getQueryFromURL(location.href);
        window.uin = params['uin'] || "777" || '';
        window.key = params['key'] || "777" || '';
        window.wxtoken = params['wxtoken'] || '';
        window.pass_ticket = params['pass_ticket'] || ''; 
        /Vj1u58888qnsOsVRuDT7uMjTWFRhE7Rrhzjb2SBlzo=
    %252FVj1u58888qnsOsVRuDT7uMjTWFRhE7Rrhzjb2SBlzo%253D
        params['pass_ticket'] = encodeURIComponent(params['pass_ticket'].html(false).html(false).replace(/\s/g,"+"));
        window.appmsg_token = "980_hmVbpDRN2ZxchWMIG6on1cBfLEYHP8387gaYnA9WiEpZqq1_3QjX2cbtzbU~";
    })();
    

"""
