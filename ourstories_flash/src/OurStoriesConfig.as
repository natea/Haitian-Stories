package
{
    /**
     * Config for URLs.  Override default values with ourstories_config.xml .
     * 
     */
    public class OurStoriesConfig
    {

        /**
         * URL for the Red5 video recorder webapp.
         */
        public static var RED5_NC_URL:String = "rtmp:/oflaDemo";
        
        /**
         * URL for the AMF gateway.
         */
        public static var AMF_NC_URL:String = 
            "http://ourstories-staging.jazkarta.com/gateway/";
        
        /**
         * URL for the FLV files, eg for FLV id 42, FLV_URL + 42 + ".flv"
         */
        public static var FLV_URL:String = 
            "http://ourstories-staging.jazkarta.com/static/flv/";
        
        /**
         * Base URL for the story, add 33/ after the url for story id 33.
         */
        public static var STORY_URL:String = 
            "http://ourstories-staging.jazkarta.com/story/";
        /**
         * Base URL for the form, used in the new workflow with the Django
         * form after the recording.
         */
        public static var STORY_RECORD_URL:String = 
            "http://ourstories-staging.jazkarta.com/story/record/";

        [Bindable]
        /**
         * Maximum number of seconds per recording. 
         * @default 180
         */
        public static var MAX_RECORD_SEC:int = 180;
        
        [Bindable]
        public static var DEBUG:Boolean = false;
        [Bindable]
        public static var RECORD_VIDEO:Boolean = false;
        
    }
}