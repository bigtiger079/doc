

setImmediate(function() {
    console.log("[*] Starting script");
    Java.perform(function() {
        var params = [];

        var SQL = Java.use("com.tencent.wcdb.database.SQLiteDatabase");
        var ContentValues = Java.use("android.content.ContentValues");
        
        var ReceiveLuckyMoneyRequest = Java.use("com.tencent.mm.plugin.luckymoney.b.ag");
        var LuckyMoneyRequest = Java.use("com.tencent.mm.plugin.luckymoney.b.ad");
        var JSONObject = Java.use("org.json.JSONObject");

        var Class = Java.use("java.lang.Class");
        var Field = Java.use("java.lang.reflect.Field");

        var CoreNetwork = Java.use("com.tencent.mm.kernel.g");
        var RequestCaller = Java.use("com.tencent.mm.ab.o");

        function getFieldByReflect(obj, fieldName) {
            var JClass = Java.cast(obj.getClass(), Class);
            var fieldO = Java.cast(JClass.getField(fieldName), Field);
            return fieldO.get(obj);
        }
        var JB = CoreNetwork.Eh();
        var network = Java.cast(getFieldByReflect(JB, "dpP"), RequestCaller);

        SQL.insert.implementation = function(tableName, str2, arg3) {
            this.insert(tableName, str2, arg3);
            console.log("[insert] -> tableName: " + tableName);
            var values = Java.cast(arg3, ContentValues);
            if (tableName != "message") {
                return;
            }
            
            var type = values.getAsInteger("type");
            console.log("[insert] -> type: " + type);
            if (type == 436207665) {
                 handleLuckyMoney(values);
            } else if(type == 1) {
            	getContent(values);
            }
        }

        ReceiveLuckyMoneyRequest.a.overload('int', 'java.lang.String', 'org.json.JSONObject').implementation = function(arg1, arg2, arg3) {
            this.a(arg1, arg2, arg3);
            var jsonObj = Java.cast(arg3, JSONObject);
            var timingIdentifier =jsonObj.getString("timingIdentifier");
            if (params.length > 0) {
                var info = params.pop();
                //得到 timingIdentifier 之后我们就需要根据之前保存的参数构造ag请求
                var request = LuckyMoneyRequest.$new(1, parseInt(info.channelid), info.sendid, info.nativeurl, "", "", info.talker, "v1.0", timingIdentifier);
                network.a(request, 0)
            }
        }

        var JString = Java.use("java.lang.String");

        function getContent(contentValues) {
        	var content = contentValues.getAsString("content");  
            console.log("[Content] -> " + content);
            var bs = stringToBytes(content);
            console.log(JString.prototype);
			var textDecoder = new TextDecoder("utf-8");
			var textEncoder = new TextEncoder("utf-8");

            console.log("[Content] -> " +textDecoder.decode(new Uint8Array(bs)));
        }

        function handleLuckyMoney(contentValues) {
            var status = contentValues.getAsInteger("status");
            if (status == 4) { 
                return;
            }
            //发送者
            var talker = contentValues.getAsString("talker");
            var isGroup = talker.match(/@chatroom$/) != null;
            var sender = contentValues.getAsInteger("isSend");
            if (sender != 0) { //自己
            }

            var content = contentValues.getAsString("content");  
            console.log(content);

            // var jContent = Java.cast(content, JString);
            console.log(content.getBytes());


            var info = parserContent(content);
            info.talker = talker;
            //根据解析的参数构造一个新的请求
            var request = ReceiveLuckyMoneyRequest.$new(parseInt(info.channelid), info.sendid, info.nativeurl, 0, "v1.0");
            //通过network发送请求
            var success = network.a(request, 0);
            //请求发送成功之后我们还需要保存这些信息, 因为发送第二个请求的时候还会用到这些信息
            if(success) {
               params.push(info); 
            }
        }
    });
});

function parserContent(content) {
    var info = {};  //用于保存解析出的信息
    //这里面目前对我们用用的信息只有nativeurl
    var matched = content.match(/<nativeurl><!\[CDATA\[(.*?)\]\]><\/nativeurl>/)
    if (matched != null) {
        info.nativeurl = matched[1];
        //接下来我们还需要解析出nativeurl里面的所有参数,同样都保存在info里面
        var p = info.nativeurl.match(/(.+?)\?(.*)/);
        if (p != null) {
            var ps = p[2].split("&");
            for (var i = 0; i < ps.length; i++) {
                var kv = ps[i].split("=");
                info[kv[0]] = kv[1];
            }
        }
    }
    
    return info;
}


function stringToBytes( str ) {  

    var ch, st, re = []; 
    for (var i = 0; i < str.length; i++ ) { 
        ch = str.charCodeAt(i);  // get char  
        st = [];                 // set up "stack"  

       do {  
            st.push( ch & 0xFF );  // push byte to stack  
            ch = ch >> 8;          // shift value down by 1 byte  
        }    

        while ( ch );  
        // add stack contents to result  
        // done because chars have "wrong" endianness  
        re = re.concat( st.reverse() ); 
    }  
    // return an array of bytes  
    return re;  
} 