/**

   Created and copyrighted by Massimo Di Pierro <massimo.dipierro@gmail.com>
   (MIT license)  

   Example:

   <script src="share.js"></script>

**/

jQuery(function(){
	var script_source = jQuery('script[src*="share.js"]').attr('src');
        var params = function(name,default_value) {
            var match = RegExp('[?&]' + name + '=([^&]*)').exec(script_source);
            return match && decodeURIComponent(match[1].replace(/\+/g, ' '))||default_value;
        }
	var path = params('static','social');
	var url = encodeURIComponent(window.location.href);
	var host =  window.location.hostname;
	var title = escape(jQuery('title').text());
	var twit = 'http://twitter.com/home?status='+title+'%20'+url;
	var facebook = 'http://www.facebook.com/sharer.php?u='+url;
	var gplus = 'https://plus.google.com/share?url='+url;
	var tbar = '<div id="socialdrawer"><span>Compartilhar<br/></span><div id="sicons"><a href="'+twit+'" target="_blank" id="twit" title="Compartilhar no twitter"><img src="'+path+'/twitter.png"  alt="Compartilhar no Twitter" width="32" height="32" /></a><a href="'+facebook+'" target="_blank" id="facebook" title="Compartilhar no Facebook"><img src="'+path+'/facebook.png"  alt="Compartilhar no facebook" width="32" height="32" /></a><a href="'+gplus+'" target="_blank" id="gplus" title="Compartilhar no Google Plus"><img src="'+path+'/gplus-32.png"  alt="Compartilhar no Google Plus" width="32" height="32" /></a></div></div>';	
	// Add the share tool bar.
	jQuery('body').append(tbar); 
	var st = jQuery('#socialdrawer');
	st.css({'opacity':'.7','z-index':'3000','background':'#FFF','border':'solid 1px #666','border-width':' 1px 0 0 1px','height':'30px','width':'130px','position':'fixed','bottom':'0','left':'0','padding':'2px 5px','overflow':'hidden','-webkit-border-top-left-radius':' 12px','-moz-border-radius-topleft':' 12px','border-top-left-radius':' 12px','-moz-box-shadow':' -3px -3px 3px rgba(0,0,0,0.5)','-webkit-box-shadow':' -3px -3px 3px rgba(0,0,0,0.5)','box-shadow':' -3px -3px 3px rgba(0,0,0,0.5)'});
	jQuery('#socialdrawer a').css({'float':'left','width':'32px','margin':'3px 2px 2px 2px','padding':'0','cursor':'pointer'});
	jQuery('#socialdrawer span').css({'float':'left','margin':'2px 3px','text-shadow':' 1px 1px 1px #FFF','color':'#444','font-size':'18px','line-height':'1em'});
        jQuery('#socialdrawer img').hide();
	// hover
	st.click(function(){
		jQuery(this).animate({height:'40px', width:'260px', opacity: 0.95}, 300);
		jQuery('#socialdrawer img').show();
	    });
	//leave
	st.mouseleave(function(){ 
	    st.animate({height:'30px', width: '130px', opacity: .7}, 300); 
	    jQuery('#socialdrawer img').hide();
	    return false;
	    }  );
    });
