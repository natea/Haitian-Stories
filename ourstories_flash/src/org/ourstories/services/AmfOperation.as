package org.ourstories.services
{

    import flash.events.NetStatusEvent;
    import flash.events.SecurityErrorEvent;
    import flash.net.NetConnection;
    import flash.net.Responder;
    
    import org.ourstories.models.FlvModel;
    
    public class AmfOperation extends Operation
    {
        
        
        private var _gateway:NetConnection;
        private var _amfCall:String;
        private var _flvModel:FlvModel;
        
        public function AmfOperation(amfCall:String, flvModel:FlvModel)
        {
            super();
            
            _amfCall = amfCall; // such as "flv.getId"
            _flvModel = flvModel; // view has reference to FlvModel and its bindable properties
            
            _gateway = new NetConnection();
            _gateway.addEventListener(NetStatusEvent.NET_STATUS, onStatus);
            _gateway.addEventListener(SecurityErrorEvent.SECURITY_ERROR, 
                onSecurityError);
            _gateway.connect(OurStoriesConfig.AMF_NC_URL);
            
        }
        
        override public function execute():void
        {
            switch (_amfCall)
            {
                case "flv.dtrace":
                    _gateway.call(_amfCall, new Responder(onResponderSuccess, 
                        onResponderFail), _flvModel.dtrace);
                    break;
                case "flv.setStatus":
                    _gateway.call(_amfCall, new Responder(onResponderSuccess, 
                        onResponderFail), _flvModel.id, _flvModel.status);
                    break;
                case "flv.setStatusType":
                    _gateway.call(_amfCall, new Responder(onResponderSuccess, 
                        onResponderFail), _flvModel.id, _flvModel.status, 
                        _flvModel.mediaType);
                    break;
                case "flv.linkFlvToStory":
                    _gateway.call(_amfCall, new Responder(onResponderSuccess, 
                        onResponderFail), _flvModel.id, _flvModel.storyId,
                        _flvModel.mediaType);
                    break;                  
                default:
                    // call with _amfCall string id and argument _flvModel
                    _gateway.call(_amfCall, new Responder(onResponderSuccess, 
                        onResponderFail));
                    break;
            }
                
        }
        
        
        // handlers for NetConnection
        private function onStatus(event:NetStatusEvent):void
        {
            trace("onStatus "+event.info.code);
            if (event.info.code == "NetConnection.Call.Failed")
            {
                onFail(event, "Unable to connect to data server.");
            }
        }
        private function onSecurityError(event:SecurityErrorEvent):void
        {
            trace("onSecurityError");
            onFail(event, "Unable to connect to data server.");
        }
        
        // handlers for Responder
        private function onResponderFail(object:Object):void
        {
            trace("onResponderFail "+object.description);
            
            onFail(null);
        }
        private function onResponderSuccess(object:Object):void
        {
            trace("onResponderSuccess");
            
            // populate bindable property on FlvModel
            // view has a reference to FlvModel
            switch(_amfCall)
            {
                case "flv.ping":
                    _flvModel.ping = String(object);
                    break;
                case "flv.getId":
                    _flvModel.id = int(object);
                    break;
                case "flv.getIdSig":
                    _flvModel.id = int(object.id);
                    _flvModel.sig = String(object.sig);
                    trace("id "+_flvModel.id);
                    trace("sig "+_flvModel.sig);
                    break;
                case "flv.dtrace":
                case "flv.setStatus":
                case "flv.setStatusType":
                case "flv.linkFlvToStory":
                    // setStatus returns True if success, False if fail
                    var success:Boolean = Boolean(object);
                    if (!success) 
                        onFail(null);
                    
                    break;
                default:
                    break;
            }
            
            onSuccess(null);
        }
        

        /**
         * Calls the "flv.ping" service. 
         */
        public static function ping(flvModel:FlvModel):Operation
        {
            return new AmfOperation("flv.ping", flvModel);
        }
        /**
         * Calls the "flv.getId" service. 
         */
        public static function getId(flvModel:FlvModel):Operation
        {
            return new AmfOperation("flv.getId", flvModel);
        }
        /**
         * Calls the "flv.getIdSig" service. 
         */
        public static function getIdSig(flvModel:FlvModel):Operation
        {
            return new AmfOperation("flv.getIdSig", flvModel);
        }
        /**
         * Calls the "flv.setStatus" service. 
         */
        public static function setStatus(flvModel:FlvModel):Operation
        {
            return new AmfOperation("flv.setStatus", flvModel);
        }
        /**
         * Calls the "flv.setStatusType" service. 
         */
        public static function setStatusType(flvModel:FlvModel):Operation
        {
            return new AmfOperation("flv.setStatusType", flvModel);
        }
        /**
         * Calls the "flv.linkFlvToStory" service. 
         */
        public static function linkFlvToStory(flvModel:FlvModel):Operation
        {
            return new AmfOperation("flv.linkFlvToStory", flvModel);
        }        
        /**
         * Calls the "flv.dtrace" service. 
         */
        public static function dtrace(flvModel:FlvModel):Operation
        {
            return new AmfOperation("flv.dtrace", flvModel);
        }        
        
    }
}