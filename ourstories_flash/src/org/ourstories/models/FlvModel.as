package org.ourstories.models
{
    
    [Bindable]
    /**
     * Flv model, representing a recording
     */
    public class FlvModel extends Model
    {
        // these match status in django flv model
        public static const STATUS_RECORDED:int = 1;
        public static const STATUS_FAIL:int = 0;
        public static const STATUS_PENDING:int = 2;
        
        // these match media type in django story model
        public static const MEDIATYPE_NONE:String = "";
        public static const MEDIATYPE_FLVV:String = "flvv";
        public static const MEDIATYPE_FLVA:String = "flva";
        // mp3 via praekelt, not really used in the recorder
        public static const MEDIATYPE_MP3:String = "mp3"; 
        
        /**
         * Unique incrementing id of the flv, used for the database primary
         * key and the filename.
         * 
         * @default -1 indicates no id yet received from IFlvService
         */
        public var id:int = -1;

        /**
         * sig the flv, used for recording first then submitting form.
         * 
         * @default empty string indicates no sig yet received from IFlvService
         */
        public var sig:String = "";

        /**
         * Test ping call. 
         */
        public var ping:String;
        
        /**
         * Recording status of Flv.
         * @default STATUS_PENDING
         */
        public var status:int = STATUS_PENDING;
        
        /**
         * Story id, retrieved via html page querystring.
         * @default -1
         */
        public var storyId:int = -1;
        
        /**
         * Media type, corresponding to media type in Django.
         * @default MEDIATYPE_NONE
         */
        public var mediaType:String = MEDIATYPE_NONE;
        
        /**
         * Trace message to Django DEBUG. 
         */
        public var dtrace:String;

    }
}
