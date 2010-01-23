package org.ourstories.net 
{
    import flash.events.EventDispatcher;
    import flash.events.NetStatusEvent;
    import flash.net.NetConnection;
    import flash.net.ObjectEncoding;
    import flash.net.SharedObject;

    public class NetConnectionManager extends EventDispatcher 
    {
        
        private var _nc:NetConnection;
        private static var _instance:NetConnectionManager;
        private static const _constructorKey:Object = new Object();
    
        /**
         * Dispatched when a NetConnection object is reporting its status or error 
         * condition.
         *
         * @eventType flash.events.NetStatusEvent.NET_STATUS
         */
        [Event(name="netStatus", type="flash.events.NetStatusEvent")]
        
        /**
         * Call <code>getInstance</code> to get singleton instance of 
         * <code>NetConnectionManager</code>.
         * 
         * @param constructorKey the private constructor key
         * @throws Error Singleton requires private constructor key.
         */
        public function NetConnectionManager(constructorKey:Object) 
        {
            if (constructorKey != _constructorKey) 
            {
                throw new Error("Singleton requires private constructor key.");
            }
        }
        
        public static function getInstance():NetConnectionManager 
        {
            if (_instance == null) 
            {
                return new NetConnectionManager(_constructorKey);
            }
            return _instance;
        }
        
        
        public function connect(url:String):void 
        {
            if (_nc == null) 
            {
                
                // use amf0, not flex amf3, with red5
                NetConnection.defaultObjectEncoding = ObjectEncoding.AMF0;
                SharedObject.defaultObjectEncoding = ObjectEncoding.AMF0;
                
                _nc = new NetConnection();
                _nc.connect(url);
                _nc.addEventListener(NetStatusEvent.NET_STATUS, onNetStatus);
                // TODO others
                
                // ReferenceError: Error #1069: Property onBWDone not found on 
                // flash.net.NetConnection and there is no default value.
                var client:Object = new Object();
                client.onBWDone = function():void 
                { 
                    //trace("onBWDone"); 
                };
                _nc.client = client;
                
            }
        }
        
        public function getConnection():NetConnection 
        {
            return _nc;
        }
        
        private function onNetStatus(event:NetStatusEvent):void 
        {
            dispatchEvent(event);
        }
        
    }

}